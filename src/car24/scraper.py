from selenium import webdriver
import time
import os


def scrape_cars24_city(url, city_name, save_path="../data/raw"):
    """
    Scrape Cars24 webpage and save HTML file for a city.

    Parameters:
    -----------
    url : str
        Cars24 city URL

    city_name : str
        Name of city

    save_path : str
        Folder where HTML file will be saved
    """

    # Create folder if not exists
    os.makedirs(save_path, exist_ok=True)


    # Open Chrome
    driver = webdriver.Chrome()

    print(f"Opening {city_name} page...")


    driver.get(url)

    time.sleep(10)


    # Scroll page to load all cars
    for i in range(50):

        driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);"
        )

        time.sleep(3)


    time.sleep(5)


    # File name
    file_name = f"cars24_{city_name}.html"


    file_path = os.path.join(
        save_path,
        file_name
    )


    # Save HTML
    with open(file_path, "w", encoding="utf-8") as f:

        f.write(driver.page_source)


    print(f"{city_name} data saved successfully")
    print(os.path.abspath(file_path))


    driver.quit()