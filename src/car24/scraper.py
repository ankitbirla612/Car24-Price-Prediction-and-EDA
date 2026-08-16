from selenium import webdriver
import time
import os
import numpy as np
import pandas as pd
import re

import time
from selenium import webdriver



def scrape_cars24_city(
    url,
    city_name,
    run_number,
    save_path="../data/raw"
):
    """
    Scrape Cars24 city page using Selenium and save
    the loaded HTML for a specific scraping run.

    Parameters
    ----------
    url : str
        Cars24 city URL.

    city_name : str
        Name of the city.

    run_number : int
        Scraping attempt number, e.g. 1, 2, 3.

    save_path : str
        Directory where HTML will be saved.

    Returns
    -------
    str
        Path of the saved HTML file.
    """

    os.makedirs(save_path, exist_ok=True)

    driver = webdriver.Chrome()

    try:

        print(
            f"\n{'=' * 60}"
        )
        print(
            f"Starting {city_name} | Run {run_number}"
        )
        print(
            f"{'=' * 60}"
        )

        driver.get(url)

        # Initial page loading
        time.sleep(10)

        previous_count = 0
        unchanged_count = 0

        max_scrolls = 100

        for i in range(max_scrolls):

            driver.execute_script(
                "window.scrollTo(1, 50000000);"
            )

            time.sleep(5)

            cards = driver.find_elements(
                "css selector",
                "a[class*='carCardWrapper']"
            )

            current_count = len(cards)

            print(
                f"{city_name} | "
                f"Run {run_number} | "
                f"Scroll {i + 1} | "
                f"Cars loaded: {current_count}"
            )

            if current_count > previous_count:

                previous_count = current_count
                unchanged_count = 0

            else:

                unchanged_count += 1

            if unchanged_count >= 5:

                print(
                    "No new cars loaded for "
                    f"{unchanged_count} consecutive scrolls."
                )

                break

        # Final wait
        time.sleep(5)

        # -----------------------------------------
        # File name
        # -----------------------------------------

        file_name = (
            f"cars24_{city_name}_roll{run_number}.html"
        )

        file_path = os.path.join(
            save_path,
            file_name
        )

        # -----------------------------------------
        # Save HTML
        # -----------------------------------------

        with open(
            file_path,
            "w",
            encoding="utf-8"
        ) as f:

            f.write(driver.page_source)

        print(
            f"\n{city_name} Run {run_number} completed."
        )

        print(
            f"Cars currently in DOM: {previous_count}"
        )

        print(
            f"HTML saved at:"
        )

        print(
            os.path.abspath(file_path)
        )

        return file_path

    finally:

        driver.quit()



def extract_car_data(soup, city_name):

    data = []

    # Find actual Cars24 car cards
    car_cards = soup.select("a.styles_carCardWrapper__sXLIp")

    print(f"{city_name}: {len(car_cards)} car cards found")

    for card in car_cards:

        text = card.get_text(" ", strip=True)

        values = [
            element.get_text(" ", strip=True)
            for element in card.find_all(["p", "span"])
            if element.get_text(" ", strip=True)
        ]

        # -------------------------
        # YEAR + NAME
        # -------------------------

        year = np.nan
        name = np.nan
        variant = np.nan

        for value in values:

            match = re.match(
                r"^(\d{4})\s+(.+)$",
                value
            )

            if match:
                year = int(match.group(1))
                name = match.group(2)

                # Variant normally comes immediately after
                # the year + car name
                index = values.index(value)

                if index + 1 < len(values):

                    possible_variant = values[index + 1]

                    if (
                        possible_variant
                        not in [
                            "Petrol",
                            "Diesel",
                            "CNG",
                            "Electric",
                            "Hybrid",
                            "Manual",
                            "Automatic"
                        ]
                        and "km" not in possible_variant.lower()
                        and not possible_variant.startswith("EMI")
                        and not re.search(
                            r"₹|â‚¹|lakh",
                            possible_variant,
                            re.I
                        )
                    ):
                        variant = possible_variant

                break


        # -------------------------
        # DRIVEN KM
        # -------------------------

        driven_km = np.nan

        match = re.search(
            r"([\d,]+)\s*km",
            text,
            re.I
        )

        if match:
            driven_km = int(
                match.group(1).replace(",", "")
            )


        # -------------------------
        # FUEL
        # -------------------------

        fuel = np.nan

        for fuel_type in [
            "Petrol",
            "Diesel",
            "CNG",
            "Electric",
            "Hybrid"
        ]:

            if fuel_type in values:
                fuel = fuel_type
                break


        # -------------------------
        # TRANSMISSION
        # -------------------------

        transmission = np.nan

        for transmission_type in [
            "Manual",
            "Automatic"
        ]:

            if transmission_type in values:
                transmission = transmission_type
                break


        # -------------------------
        # REGISTRATION
        # -------------------------

        registration = np.nan

        for value in values:

            if re.fullmatch(
                r"[A-Z]{2}[-\s]?\d{1,2}",
                value
            ):
                registration = value
                break


        # -------------------------
        # EMI
        # -------------------------

        emi = np.nan

        match = re.search(
            r"EMI.*?([\d,]+)\s*/m",
            text,
            re.I
        )

        if match:

            emi = int(
                match.group(1).replace(",", "")
            )


        # -------------------------
        # PRICE
        # -------------------------

        price = np.nan

        price_matches = re.findall(
            r"(?:₹|â‚¹)\s*([\d,.]+)\s*(lakh|L)",
            text,
            re.I
        )

        if price_matches:

            # The last lakh value is the selling price
            value, unit = price_matches[-1]

            price = float(
                value.replace(",", "")
            ) * 100000


        # -------------------------
        # LOCATION
        # -------------------------

        location = np.nan

        location_element = card.select_one(
            "div.styles_hubAddress__URioy"
        )

        if location_element:

            location = location_element.get_text(
                " ",
                strip=True
            )


        # -------------------------
        # CITY
        # -------------------------

        city = city_name


        # -------------------------
        # STORE DATA
        # -------------------------

        data.append({
            "year": year,
            "name": name,
            "variant": variant,
            "price": price,
            "emi": emi,
            "driven_km": driven_km,
            "fuel": fuel,
            "transmission": transmission,
            "registration": registration,
            "location": location,
            "city": city
        })


    return pd.DataFrame(data)
