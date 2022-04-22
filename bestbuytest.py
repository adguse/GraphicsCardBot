import bs4
import sys
import time
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException, TimeoutException, \
    WebDriverException, ElementClickInterceptedException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC, wait
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager

# ---------------------------------------------Please Read--------------------------------------------------------------

# Updated: 4/12/2021

# Hello everyone! Welcome to my Best Buy script.
# Let's go over the checklist for the script to run properly.
#   1. Product URL
#   2. Firefox Profile
#   3. Credit Card CVV Number
#   4. Twilio Account

# This Script only accepts Product URL's that look like this. I hope you see the difference between page examples.

# Example 1 - Nvidia RTX 3080:
# https://www.bestbuy.com/site/nvidia-geforce-rtx-3080-10gb-gddr6x-pci-express-4-0-graphics-card-titanium-and-black/6429440.p?skuId=6429440
# Example 2 - PS5:
# https://www.bestbuy.com/site/sony-playstation-5-console/6426149.p?skuId=6426149
# Example 3 - Ryzen 5600x:
# https://www.bestbuy.com/site/amd-ryzen-5-5600x-4th-gen-6-core-12-threads-unlocked-desktop-processor-with-wraith-stealth-cooler/6438943.p?skuId=6438943

# This Script does not accept Product URL's that look like this.
# https://www.bestbuy.com/site/searchpage.jsp?st=rtx+3080&_dyncharset=UTF-8&_dynSessConf=&id=pcat17071&type=page&sc=Global&cp=1&nrp=&sp=&qp=&list=n&af=true&iht=y&usc=All+Categories&ks=960&keys=keys

# Highly Recommend To set up Twilio Account to receive text messages. So if bot doesn't work you'll at least get a phone
# text message with the url link. You can click the link and try manually purchasing on your phone.

# Twilio is free. Get it Here.
# www.twilio.com/referral/BgLBXx

# -----------------------------------------------Steps To Complete------------------------------------------------------

# Test Link 1 - Ryzen 5800x seems to be available quite often. It is the best URL to try out preorder script.
# To actually avoid buying CPU, you can comment out Line 220. Uncomment the line when you are done testing.
# https://www.bestbuy.com/site/amd-ryzen-7-5800x-4th-gen-8-core-16-threads-unlocked-desktop-processor-without-cooler/6439000.p?skuId=6439000

# Test Link 2 (cheap HDMI cable) - https://www.bestbuy.com/site/dynex-6-hdmi-cable-black/6405508.p?skuId=6405508
# *Warning* - Script will try to checkout the HDMI cable twice since this is how the Bestbuy preorder script works
# Best buy makes us click the add to cart button twice to enter Queue System. 
# Don't worry about script buying two graphics cards though. The script will only buy one.
# As well, Best buy won't let you check out more than 1 item.
# To actually avoid buying HDMI cable, you can comment out Line 220. Uncomment the line when you are done testing.

# 1. Product URL
url = 'https://www.bestbuy.com/site/nvidia-geforce-rtx-3080-10gb-gddr6x-pci-express-4-0-graphics-card-titanium-and-black/6429440.p?skuId=6429440'


# 2. Firefox Profile
def create_driver():
    """Creating firefox driver to control webpage. Please add your firefox profile here."""
    options = Options()
    options.headless = False  # Change To False if you want to see Firefox Browser Again.
    web_driver = webdriver.Chrome()#webdriver.Firefox(options=options)
    return web_driver


# 3. credit card CVV Number
CVV = ''  # You can enter your CVV number here in quotes.
email = ''
password = ''

# 4. Twilio Account
toNumber = ''
fromNumber = ''
accountSid = ''
authToken = ''
client = Client(accountSid, authToken)

# ----------------------------------------------------------------------------------------------------------------------


def time_sleep(x, driver):
    """Sleep timer for page refresh."""
    for i in range(x, -1, -1):
        sys.stdout.write('\r')
        sys.stdout.write('{:2d} seconds'.format(i))
        sys.stdout.flush()
        time.sleep(1)
    #driver.execute_script('window.localStorage.clear();')
    driver.refresh()


def extract_page():
    html = driver.page_source
    soup = bs4.BeautifulSoup(html, 'html.parser')
    return soup


def driver_click(driver, find_type, selector):
    """Driver Wait and Click Settings."""
    while True:
        if find_type == 'css':
            try:
                driver.find_element_by_css_selector(selector).click()
                break
            except NoSuchElementException:
                driver.implicitly_wait(1)
        elif find_type == 'name':
            try:
                driver.find_element_by_name(selector).click()
                break
            except NoSuchElementException:
                driver.implicitly_wait(1)
        elif find_type == 'xpath':
            try:
                driver.find_element_by_xpath(f"//*[@class='{selector}']").click()
                break
            except NoSuchElementException:
                driver.implicitly_wait(1)

def login(driver,wait):
    try:
        print("\nLogging in.\n")

        
        wait.until(EC.presence_of_element_located((By.ID, "fld-p1")))
        time.sleep(1)
        passs = driver.find_element_by_id("fld-p1")
        time.sleep(1)
        passs.send_keys(password)
        time.sleep(1)
        wait.until(EC.presence_of_element_located((By.ID, "fld-e")))
        time.sleep(3)
        emails = driver.find_element_by_id("fld-e")
        time.sleep(1)
        emails.send_keys(email)
        driver_click(driver, 'css', '.cia-form__controls__submit')
    except (NoSuchElementException, TimeoutException) as error:
        print(f'Login error: ${error}')


def searching_for_card(driver):
    """Scanning for card."""
    driver.get(url)
    while True:
        soup = extract_page()
        wait = WebDriverWait(driver, 15)
        wait2 = WebDriverWait(driver, 5)

        try:
            add_to_cart_button = soup.find('button', {
                'class': 'btn btn-primary btn-lg btn-block btn-leading-ficon add-to-cart-button'})

            if add_to_cart_button:
                print(f'Add To Cart Button Found!')

                # Queue System Logic.
                try:
                    # Entering Queue: Clicking "add to cart" 2nd time to enter queue.
                    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".add-to-cart-button")))
                    driver_click(driver, 'css', '.add-to-cart-button')
                    print("Clicked Add to Cart Button. Now sending message to your phone.")
                    print("You are now added to Best Buy's Queue System. Page will be refreshing. Please be patient.")

                    # Sleep timer is here to give Please Wait Button to appear. Please don't edit this.
                    time.sleep(3)
                except (NoSuchElementException, TimeoutException) as error:
                    print(f'Queue System Error: ${error}')

                # Sending Text Message To let you know you are in the queue system.
                try:
                    client.messages.create(to=toNumber, from_=fromNumber,
                                           body=f'Your In Queue System on Bestbuy! {url}')
                except (NameError, TwilioRestException):
                    pass

                in_cart = driver.find_element_by_xpath("/html/body/div[2]/div/div[1]/header/div[1]/div/div[3]/div[1]/div/div/div/div/a/div")
                if not in_cart:
                    print('In Q')
                    # In queue, just waiting for "add to cart" button to turn clickable again.
                    # page refresh every 15 seconds until Add to Cart button reappears.
                    while True:
                        try:
                            driver.refresh()
                            time.sleep(5)
                            add_to_cart = driver.find_element_by_css_selector(".add-to-cart-button")
                            please_wait_enabled = add_to_cart.get_attribute('aria-describedby')

                            if please_wait_enabled:
                                time.sleep(5)
                            else:  # When Add to Cart appears. This will click button.
                                print("Add To Cart Button Clicked A Second Time.")
                                wait2.until(
                                    EC.presence_of_element_located((By.CSS_SELECTOR, ".add-to-cart-button")))
                                time.sleep(2)
                                driver_click(driver, 'css', '.add-to-cart-button')
                                time.sleep(2)
                            in_cart = driver.find_element_by_xpath("/html/body/div[2]/div/div[1]/header/div[1]/div/div[3]/div[1]/div/div/div/div/a/div")
                            if in_cart:
                                break
                        except(NoSuchElementException, TimeoutException) as error:
                            print(f'Queue System Refresh Error: ${error}')

                # Going To Cart Process.
                driver.get('https://www.bestbuy.com/cart')

                # Checking if item is still in cart.
                try:
                    wait.until(
                        EC.presence_of_element_located((By.XPATH, "//*[@class='btn btn-lg btn-block btn-primary']")))
                    time.sleep(1)
                    driver_click(driver, 'xpath', 'btn btn-lg btn-block btn-primary')
                    print("Item Is Still In Cart.")
                except (NoSuchElementException, TimeoutException):
                    print("Item is not in cart anymore. Retrying..")
                    time_sleep(3, driver)
                    searching_for_card(driver)

                # Logging Into Account.
                print("Attempting to Login. Firefox should remember your login info to auto login.")

                try:
                    print("\nLogging in.\n")
                    wait.until(EC.presence_of_element_located((By.ID, "fld-p1")))
                    time.sleep(1)
                    passs = driver.find_element_by_id("fld-p1")
                    time.sleep(1)
                    passs.send_keys(password)
                    time.sleep(1)
                    wait.until(EC.presence_of_element_located((By.ID, "fld-e")))
                    time.sleep(3)
                    emails = driver.find_element_by_id("fld-e")
                    time.sleep(1)
                    emails.send_keys(email)
                    driver_click(driver, 'css', '.cia-form__controls__submit')
                except (NoSuchElementException, TimeoutException, Exception) as error:
                    print(f'Login error: ${error}')



                # second login
                try:
                    print("\nSecond Login.\n")
                    wait2.until(EC.presence_of_element_located((By.ID, "fld-p1")))
                    time.sleep(1)
                    security_code = driver.find_element_by_id("fld-p1")
                    time.sleep(1)
                    security_code.send_keys(password)
                except (NoSuchElementException, TimeoutException, Exception):
                    pass

                #second sign in
                try:
                    wait2.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/section/main/div[2]/div[1]/div/div/div/div/form/div[3]/button")))
                    time.sleep(2)
                    sign_in = driver.find_element_by_xpath("/html/body/div[1]/div/section/main/div[2]/div[1]/div/div/div/div/form/div[3]/button")
                    sign_in.click()
                    print("Clicking Sign in.")
                except (NoSuchElementException, TimeoutException, ElementNotInteractableException, ElementClickInterceptedException, Exception) as error:
                    print(f'sign in error: {error}')

                

                # Click Shipping Option. (if available)
                try:
                    wait2.until(EC.presence_of_element_located((By.XPATH, "//*[@class='btn btn-lg btn-block btn-primary button__fast-track']")))
                    time.sleep(2)
                    shipping_class = driver.find_element_by_xpath("//*[@class='ispu-card__switch']")
                    shipping_class.click()
                    print("Clicking Shipping Option.")
                except (NoSuchElementException, TimeoutException, ElementNotInteractableException, ElementClickInterceptedException, Exception) as error:
                    print(f'shipping error: {error}')

                time.sleep(1)
                # Trying CVV
                try:
                    print("\nTrying CVV Number.\n")
                    wait2.until(EC.presence_of_element_located((By.ID, "credit-card-cvv")))
                    time.sleep(2)
                    security_code = driver.find_element_by_id("credit-card-cvv")
                    security_code.send_keys(CVV)
                except (NoSuchElementException, TimeoutException, Exception):
                    pass

                # Final Checkout.
                try:
                    wait2.until(EC.presence_of_element_located((By.XPATH, "//*[@class='btn btn-lg btn-block btn-primary button__fast-track']")))
                    print("clicked checkout")
                    # comment the line down below to avoid buying when testing bot. vv
                    driver_click(driver, 'xpath', 'btn btn-lg btn-block btn-primary button__fast-track')  
                except (NoSuchElementException, TimeoutException, ElementNotInteractableException):
                    print("Could Not Complete Checkout.")

                # Completed Checkout.
                print('Order Placed!')
                time.sleep(1800)
                driver.quit()

        except (NoSuchElementException, TimeoutException) as error:
            print(f'error is: {error}')

        time_sleep(3, driver)


if __name__ == '__main__':
    #url = input("Enter bestbuy website link: ")
   # url = sys.argv[1]
    driver = create_driver()
    #login(driver)
    searching_for_card(driver)
