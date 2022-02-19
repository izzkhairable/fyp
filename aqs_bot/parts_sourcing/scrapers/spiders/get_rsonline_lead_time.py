from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def get_rsonline_lead_time(url):
    try:
        driver = webdriver.Chrome(
            executable_path=r"C:\Users\Izzat Khair\Downloads\chromedriver_win32\chromedriver.exe"
        )
        driver.get(url)

        driver.title

        driver.implicitly_wait(5)

        button = driver.find_element(
            By.XPATH,
            "/html/body/div[14]/div/main/div[1]/div[2]/div[2]/div/form/p/button",
        )

        button.click()
        wait = WebDriverWait(driver, 5)
        element = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "/html/body/div[15]/div/div/section/div/div[2]/button")
            )
        )

        input_box = driver.find_element(
            By.XPATH,
            "/html/body/div[15]/div/div/section/div[1]/div[1]/div[2]/div[1]/input",
        )
        input_box.send_keys("0000000")

        element.click()
        wait2 = WebDriverWait(driver, 5)
        element2 = wait2.until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    '//div[@color="Amber"]',
                )
            )
        )
        raw_lead_time = element2.get_attribute("innerHTML")
        print("raw_lead_time", raw_lead_time)

        driver.quit()
        return raw_lead_time
    except:
        return None
