#import pkg_resources
#driverPath=pkg_resources.resource_filename(__name__, "chromedriver.exe")
#from seleniumwire import webdriver
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
#try:
 #   svc = Service(ChromeDriverManager().install())
#except:
 #   svc = None
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException, NoSuchElementException
#service = Service(service_args=["--disable-build-check"])


class Driver:
    """
    Initializes a webdriver instance with specified configurations.

    Args:
        headless (bool, optional): Whether to run the webdriver in headless mode (no browser window). Defaults to True.
        user_agent (bool, optional):  Whether to use a custom user agent.  If True, a default user agent will be used (implementation details not specified here). Defaults to False.
        window_size (str, optional): The size of the browser window in the format "width,height". Defaults to "1400,1800".

    Returns:
        None
    """
    def __init__(self, 
                 headless=True, 
                 user_agent=False, 
                 window_size="1400,1800", 
                 executable_path = False, 
                 add_svc=False, 
                 verbose:bool=True,
                fetch_requests:bool=False):
        """
        args
            headless : Bool
                Set headless as True to go headless
            user_agent : Bool
                Set user agent as True to add user agents to options
                Setting as True may cause problems during google search
        """
        self.headless = headless
        self.user_agent = user_agent
        self.window_size = window_size
        self._driver = None
        self.verbose = verbose
        self.executable_path = executable_path
        self.add_svc = add_svc
        self.fetch_requests = fetch_requests
        
        return None
    
    def get_driver(self, download_directory=None, options=Options(), **kwargs):
        """Initializes and returns a Chrome webdriver instance with specified options.

    This function creates a Chrome webdriver, configuring it with various options 
    based on the object's attributes and provided arguments.  It handles window size, 
    headless mode, user agent, download directory settings, and anti-bot measures.

    Args:
        download_directory (str, optional): The directory where downloads should be saved. 
                                        Defaults to None.
        options (webdriver.chrome.options.Options, optional):  Pre-configured webdriver 
                                                            options. Defaults to Options().
        **kwargs: Additional keyword arguments are ignored.

    Returns:
        webdriver.Chrome: A configured Chrome webdriver instance.

    Notes:
        - The function uses the object's `self.window_size`, `self.headless`, and `self.user_agent` 
        attributes to configure the webdriver.  Ensure these attributes are correctly set before calling.
        -  If `download_directory` is provided, it configures the webdriver to automatically 
        download files to that location without prompting the user.
        -  Anti-bot measures, such as disabling the 'AutomationControlled' blink feature, 
        are included to help avoid detection as a bot.
        - The webdriver is configured to detach from the session after initialization, preventing it from closing automatically.

    """
        
        if self.executable_path:
            if self.verbose:
                print("Adding chrome executable path to options....")
            #options.binary_location = _execPath
            if self.verbose:
                print("Executable path set for options binary location")

        if self.window_size:
            if self.verbose:
                print(f"Setting the window size to : {self.window_size}....") 
            options.add_argument(f"window-size={self.window_size}")
            options.add_argument("--start-maximized")
            if self.verbose:
                print("The window size has been set")
        if self.headless:
            if self.verbose:
                print("Going headless....")
            options.add_argument("--headless")#causes blank white window
            # https://stackoverflow.com/questions/78996364/chrome-129-headless-shows-blank-window
            #options.add_argument("--headless=old")
            if self.verbose:
                print("Gone headless")
        if self.user_agent:
            if self.verbose:
                print("Adding user agent....")
            user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.517 Safari/537.36'
            options.add_argument('user-agent={0}'.format(user_agent))
            if self.verbose:
                print(f"User agent has been added")
            
        options.add_experimental_option("detach", True)
        # To avoid detection as a bot
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument("--disable-gpu")
        #options.add_argument("user-data-dir=selenium")

        if download_directory:
            options.add_experimental_option('prefs',  {
                "download.default_directory": download_directory,
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "plugins.always_open_pdf_externally": True
                }
            )
        
        if self.add_svc:
            try:
                svc = Service(ChromeDriverManager().install())
            except Exception as e:
                print(f"Error adding svc \n\t{e}")
                svc = None
        else:
            svc=None 
        
        if self.fetch_requests:
            from seleniumwire import webdriver

            return webdriver.Chrome(options=options, service=svc)
        
        from selenium import webdriver
        return webdriver.Chrome(options=options, service=svc)
    
    def driver(self, download_directory=None, options=Options(), **kwargs):
        if self._driver is None:
            self._driver = self.get_driver(download_directory, options, **kwargs)
        return self._driver


def START(url, **kwargs):
    """Initializes a webdriver and navigates to a given URL.

    Args:
        url (str): The URL to navigate to.
        **kwargs: Keyword arguments passed to the Driver class.  
                  These arguments are typically used to customize the webdriver 
                  (e.g., setting specific browser options).

    Returns:
        tuple: A tuple containing the initialized webdriver and a WebDriverWait object.
               The WebDriverWait object is configured with a 10-second timeout.

    Raises:
        (Implicitly):  Any exceptions raised by the Driver class or webdriver during initialization or navigation.
    """
    verbose = True if kwargs.get("verbose") else False
    if verbose: 
        print("="*127)
        print("Initiating the driver")
    driver = Driver(**kwargs).driver()
    wait = WebDriverWait(driver, 10)
    if verbose:
        print("The driver was initialised")
        print(f"Opening the site from {url}")
    driver.get(url)
    if verbose:
        print("The site was opened")
    return driver, wait

def END(driver, **kwargs):
    """Closes the webdriver instance gracefully.

    This function closes and quits the provided webdriver, ensuring all resources are released.  It prints messages to the console indicating the process.

    Args:
        driver: The webdriver instance (e.g., from selenium) to be closed.

    Returns:
        None.
    """
    verbose = True if kwargs.get("verbose") else False 
    if verbose:
        print("Closing the driver")
    driver.close()
    driver.quit()
    if verbose:
        print("The driver was closed")
        print("="*127)
    return None

