import os
import pickle
from time import sleep
from typing import Optional

from rich import print

from libs import WebScraping


class FactoryScraper(WebScraping):
    def __init__(
        self,
        username: Optional[str],
        password: Optional[str],
        keywords: list,
        headless: bool = False,
        wait_time: int = 60,
    ) -> None:
        """starts chrome and initializes the scraper

        args:
            username: (str) username from .env
            password: (str) passsword from .env
            keywords: (list, str) filter titles for the targeted orders.
            headless: (bool) enables headless mode.
        """

        # start scraper class
        super().__init__(headless=headless)

        # credentials
        self.username = username
        self.password = password

        # Title filter
        self.keywords = keywords
        
        # Refresh time
        self.wait_time = wait_time

        self.extracted_orders = {}

    def __login__(self) -> None:
        """checks if session cookies exists

        if the cookies are found load them
        ifnot perfoms login.
        """

        self.set_page("https://www.boostingfactory.com/login")

        sleep(3)
        self.refresh_selenium()

        selectors = {
            "username": "#uName",
            "password": "#uPassword",
            "submit": "button[type='submit']",
        }

        # search for local cookies
        if os.path.exists("cookies.pkl"):
            # if cookies are found load them
            with open("cookies.pkl", "rb") as file:
                cookies = pickle.load(file)
                
                self.__load_cookies__(cookies)
                self.refresh_selenium()
                
            # Validate login cookies
            current_page = self.driver.current_url
            if "login" in current_page:
                print("Login failed. Posible cookies expired. Traying again...")
                
                # Delete cookies file
                if os.path.exists("cookies.pkl"):
                    os.remove("cookies.pkl")
                
                # Try login again
                self.__login__()
                
                return None
            else:
                print("Login successful.")
                return None
                        
        # if cookies doesn't exists do login
        username = self.get_elem(selectors["username"])
        username.send_keys(self.username)

        password = self.get_elem(selectors["password"])
        password.send_keys(self.password)

        self.click_js(selectors["submit"])
        
        # Validate login credentials
        current_page = self.driver.current_url
        if "login" in current_page:
            print("Login failed. Check credentials and try again.")                
            quit()
        else:
            print("Login successful.")

        # store cookies
        cookies = self.get_browser().get_cookies()
        with open("cookies.pkl", "wb") as file:
            pickle.dump(cookies, file)

    def __load_cookies__(self, cookies) -> None:
        """Load cookies into the current session."""
        for cookie in cookies:
            self.driver.add_cookie(cookie)

        self.set_page("https://www.boostingfactory.com/profile")
        self.zoom(50)

    def __loop_orders__(self) -> None:
        """Loop through orders and stores it to be processed later."""

        selectors = {
            "orders_tab": ".orders .nav.nav-tabs > li:first-child a",
            "orders": "div#availableOrders .orders-preloader + div",
            "order_button": "div#availableOrders div.single-order' \
                '.order-detail-btn .btn-for-bright",
            "order_link": "a",
            "order_title": "h3",
            "order_accept": "button.btn.order-accept-btn.btn-for-bright",
            "order_ok": ".answer-btn",
        }

        # Move to orders tab
        self.click_js(selectors["orders_tab"])
        self.refresh_selenium(time_units=0.1)

        orders = self.get_elems(selectors["orders"])

        orders_accepted = 0
        for order in range(0, len(orders)):

            # Validate order title
            selector_order = f"{selectors['orders']}:nth-child({(order + 1)*2})"
            selector_title = f"{selector_order} {selectors['order_title']}"
            title = self.get_text(selector_title)
            target = self.__filter__(title)

            if not target:
                continue

            # Accept order
            self.click_js(f"{selector_order} {selectors['order_accept']}")
            self.refresh_selenium()
            self.click_js(f"{selectors['order_ok']}")

            print(f"Order {title} accepted")
            orders_accepted += 1

        print(f"Total orders accepted: {orders_accepted}")

    def __filter__(self, title) -> bool:
        """Filter keywords from order titles.

        Args:
            title: (str) title keyword

        Returns: boolean
        """

        for keyword in self.keywords:
            if keyword.strip().lower() == str(title).strip().lower():
                return True
        return False

    def __retrieve_new_orders__(self) -> None:
        """Search for new orders."""
        self.set_page("https://www.boostingfactory.com/profile")

    def automate_orders(self) -> None:
        """automate accepting orders."""

        self.__login__()

        while True:

            # Loop available orders and accept by title
            self.__loop_orders__()

            # Wait 1 minute
            print(f"waiting {self.wait_time} milliseconds")
            sleep(self.wait_time/1000)
