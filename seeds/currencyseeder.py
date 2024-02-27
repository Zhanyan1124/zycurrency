from flask_seeder import Seeder
from apps.models import Currency
from apps import db
from flask import current_app 
import json
import requests

class CurrencySeeder(Seeder):
  def __init__(self, db=None):
    super().__init__(db=db)
    self.priority = 1

  def run(self):
    currency_data = {
      "AED": {"name": "United Arab Emirates Dirham", "alpha_2_code": "AE"},
      "AFN": {"name": "Afghan Afghani", "alpha_2_code": "AF"},
      "ALL": {"name": "Albanian Lek", "alpha_2_code": "AL"},
      "AMD": {"name": "Armenian Dram", "alpha_2_code": "AM"},
      "ANG": {"name": "Dutch Guilder", "alpha_2_code": "AN"},
      "AOA": {"name": "Angolan Kwanza", "alpha_2_code": "AO"},
      "ARS": {"name": "Argentine Peso", "alpha_2_code": "AR"},
      "AUD": {"name": "Australian Dollar", "alpha_2_code": "AU"},
      "AWG": {"name": "Aruban Florin", "alpha_2_code": "AW"},
      "AZN": {"name": "Azerbaijani Manat", "alpha_2_code": "AZ"},
      "BAM": {"name": "Bosnia-Herzegovina Convertible Mark", "alpha_2_code": "BA"},
      "BBD": {"name": "Barbadian Dollar", "alpha_2_code": "BB"},
      "BDT": {"name": "Bangladeshi Taka", "alpha_2_code": "BD"},
      "BGN": {"name": "Bulgarian Lev", "alpha_2_code": "BG"},
      "BHD": {"name": "Bahraini Dinar", "alpha_2_code": "BH"},
      "BIF": {"name": "Burundian Franc", "alpha_2_code": "BI"},
      "BMD": {"name": "Bermudian Dollar", "alpha_2_code": "BM"},
      "BND": {"name": "Bruneian Dollar", "alpha_2_code": "BN"},
      "BOB": {"name": "Bolivian Boliviano", "alpha_2_code": "BO"},
      "BRL": {"name": "Brazilian Real", "alpha_2_code": "BR"},
      "BSD": {"name": "Bahamian Dollar", "alpha_2_code": "BS"},
      "BTN": {"name": "Bhutanese Ngultrum", "alpha_2_code": "BT"},
      "BWP": {"name": "Botswanan Pula", "alpha_2_code": "BW"},
      "BZD": {"name": "Belizean Dollar", "alpha_2_code": "BZ"},
      "CAD": {"name": "Canadian Dollar", "alpha_2_code": "CA"},
      "CDF": {"name": "Congolese Franc", "alpha_2_code": "CD"},
      "CHF": {"name": "Swiss Franc", "alpha_2_code": "CH"},
      "CLF": {"name": "Chilean Unit of Account UF", "alpha_2_code": "CL"},
      "CLP": {"name": "Chilean Peso", "alpha_2_code": "CL"},
      "CNH": {"name": "Chinese Yuan Offshore", "alpha_2_code": "CN"},
      "CNY": {"name": "Chinese Yuan", "alpha_2_code": "CN"},
      "COP": {"name": "Colombian Peso", "alpha_2_code": "CO"},
      "CUP": {"name": "Cuban Peso", "alpha_2_code": "CU"},
      "CVE": {"name": "Cape Verdean Escudo", "alpha_2_code": "CV"},
      "CZK": {"name": "Czech Republic Koruna", "alpha_2_code": "CZ"},
      "DJF": {"name": "Djiboutian Franc", "alpha_2_code": "DJ"},
      "DKK": {"name": "Danish Krone", "alpha_2_code": "DK"},
      "DOP": {"name": "Dominican Peso", "alpha_2_code": "DO"},
      "DZD": {"name": "Algerian Dinar", "alpha_2_code": "DZ"},
      "EGP": {"name": "Egyptian Pound", "alpha_2_code": "EG"},
      "ERN": {"name": "Eritrean Nakfa", "alpha_2_code": "ER"},
      "ETB": {"name": "Ethiopian Birr", "alpha_2_code": "ET"},
      "EUR": {"name": "Euro", "alpha_2_code": "EU"},
      "FJD": {"name": "Fijian Dollar", "alpha_2_code": "FJ"},
      "FKP": {"name": "Falkland Islands Pound", "alpha_2_code": "FK"},
      "GBP": {"name": "British Pound Sterling", "alpha_2_code": "GB"},
      "GEL": {"name": "Georgian Lari", "alpha_2_code": "GE"},
      "GHS": {"name": "Ghanaian Cedi", "alpha_2_code": "GH"},
      "GIP": {"name": "Gibraltar Pound", "alpha_2_code": "GI"},
      "GMD": {"name": "Gambian Dalasi", "alpha_2_code": "GM"},
      "GNF": {"name": "Guinean Franc", "alpha_2_code": "GN"},
      "GTQ": {"name": "Guatemalan Quetzal", "alpha_2_code": "GT"},
      "GYD": {"name": "Guyanaese Dollar", "alpha_2_code": "GY"},
      "HKD": {"name": "Hong Kong Dollar", "alpha_2_code": "HK"},
      "HNL": {"name": "Honduran Lempira", "alpha_2_code": "HN"},
      "HRK": {"name": "Croatian Kuna", "alpha_2_code": "HR"},
      "HTG": {"name": "Haitian Gourde", "alpha_2_code": "HT"},
      "HUF": {"name": "Hungarian Forint", "alpha_2_code": "HU"},
      "IDR": {"name": "Indonesian Rupiah", "alpha_2_code": "ID"},
      "ILS": {"name": "Israeli New Sheqel", "alpha_2_code": "IL"},
      "INR": {"name": "Indian Rupee", "alpha_2_code": "IN"},
      "IQD": {"name": "Iraqi Dinar", "alpha_2_code": "IQ"},
      "IRR": {"name": "Iranian Rial", "alpha_2_code": "IR"},
      "ISK": {"name": "Icelandic Krona", "alpha_2_code": "IS"},
      "JMD": {"name": "Jamaican Dollar", "alpha_2_code": "JM"},
      "JOD": {"name": "Jordanian Dinar", "alpha_2_code": "JO"},
      "JPY": {"name": "Japanese Yen", "alpha_2_code": "JP"},
      "KES": {"name": "Kenyan Shilling", "alpha_2_code": "KE"},
      "KGS": {"name": "Kyrgyzstani Som", "alpha_2_code": "KG"},
      "KHR": {"name": "Cambodian Riel", "alpha_2_code": "KH"},
      "KMF": {"name": "Comorian Franc", "alpha_2_code": "KM"},
      "KPW": {"name": "North Korean Won", "alpha_2_code": "KP"},
      "KRW": {"name": "South Korean Won", "alpha_2_code": "KR"},
      "KWD": {"name": "Kuwaiti Dinar", "alpha_2_code": "KW"},
      "KYD": {"name": "Caymanian Dollar", "alpha_2_code": "KY"},
      "KZT": {"name": "Kazakhstani Tenge", "alpha_2_code": "KZ"},
      "LAK": {"name": "Laotian Kip", "alpha_2_code": "LA"},
      "LBP": {"name": "Lebanese Pound", "alpha_2_code": "LB"},
      "LKR": {"name": "Sri Lankan Rupee", "alpha_2_code": "LK"},
      "LRD": {"name": "Liberian Dollar", "alpha_2_code": "LR"},
      "LSL": {"name": "Basotho Maloti", "alpha_2_code": "LS"},
      "LYD": {"name": "Libyan Dinar", "alpha_2_code": "LY"},
      "MAD": {"name": "Moroccan Dirham", "alpha_2_code": "MA"},
      "MDL": {"name": "Moldovan Leu", "alpha_2_code": "MD"},
      "MGA": {"name": "Malagasy Ariary", "alpha_2_code": "MG"},
      "MKD": {"name": "Macedonian Denar", "alpha_2_code": "MK"},
      "MMK": {"name": "Myanma Kyat", "alpha_2_code": "MM"},
      "MNT": {"name": "Mongolian Tugrik", "alpha_2_code": "MN"},
      "MOP": {"name": "Macanese Pataca", "alpha_2_code": "MO"},
      "MRU": {"name": "Mauritanian Ouguiya", "alpha_2_code": "MR"},
      "MUR": {"name": "Mauritian Rupee", "alpha_2_code": "MU"},
      "MVR": {"name": "Maldivian Rufiyaa", "alpha_2_code": "MV"},
      "MWK": {"name": "Malawian Kwacha", "alpha_2_code": "MW"},
      "MXN": {"name": "Mexican Peso", "alpha_2_code": "MX"},
      "MYR": {"name": "Malaysian Ringgit", "alpha_2_code": "MY"},
      "MZN": {"name": "Mozambican Metical", "alpha_2_code": "MZ"},
      "NAD": {"name": "Namibian Dollar", "alpha_2_code": "NA"},
      "NGN": {"name": "Nigerian Naira", "alpha_2_code": "NG"},
      "NOK": {"name": "Norwegian Krone", "alpha_2_code": "NO"},
      "NPR": {"name": "Nepalese Rupee", "alpha_2_code": "NP"},
      "NZD": {"name": "New Zealand Dollar", "alpha_2_code": "NZ"},
      "OMR": {"name": "Omani Rial", "alpha_2_code": "OM"},
      "PAB": {"name": "Panamanian Balboa", "alpha_2_code": "PA"},
      "PEN": {"name": "Peruvian Nuevo Sol", "alpha_2_code": "PE"},
      "PGK": {"name": "Papua New Guinean Kina", "alpha_2_code": "PG"},
      "PHP": {"name": "Philippine Peso", "alpha_2_code": "PH"},
      "PKR": {"name": "Pakistani Rupee", "alpha_2_code": "PK"},
      "PLN": {"name": "Polish Zloty", "alpha_2_code": "PL"},
      "PYG": {"name": "Paraguayan Guarani", "alpha_2_code": "PY"},
      "QAR": {"name": "Qatari Rial", "alpha_2_code": "QA"},
      "RON": {"name": "Romanian Leu", "alpha_2_code": "RO"},
      "RSD": {"name": "Serbian Dinar", "alpha_2_code": "RS"},
      "RUB": {"name": "Russian Ruble", "alpha_2_code": "RU"},
      "RWF": {"name": "Rwandan Franc", "alpha_2_code": "RW"},
      "SAR": {"name": "Saudi Arabian Riyal", "alpha_2_code": "SA"},
      "SCR": {"name": "Seychellois Rupee", "alpha_2_code": "SC"},
      "SDG": {"name": "Sudanese Pound", "alpha_2_code": "SD"},
      "SEK": {"name": "Swedish Krona", "alpha_2_code": "SE"},
      "SGD": {"name": "Singapore Dollar", "alpha_2_code": "SG"},
      "SHP": {"name": "Saint Helena Pound", "alpha_2_code": "SH"},
      "SLL": {"name": "Sierra Leonean Leone", "alpha_2_code": "SL"},
      "SOS": {"name": "Somali Shilling", "alpha_2_code": "SO"},
      "SRD": {"name": "Surinamese Dollar", "alpha_2_code": "SR"},
      "SYP": {"name": "Syrian Pound", "alpha_2_code": "SY"},
      "SZL": {"name": "Swazi Emalangeni", "alpha_2_code": "SZ"},
      "THB": {"name": "Thai Baht", "alpha_2_code": "TH"},
      "TJS": {"name": "Tajikistani Somoni", "alpha_2_code": "TJ"},
      "TMT": {"name": "Turkmenistani Manat", "alpha_2_code": "TM"},
      "TND": {"name": "Tunisian Dinar", "alpha_2_code": "TN"},
      "TOP": {"name": "Tongan Pa'anga", "alpha_2_code": "TO"},
      "TRY": {"name": "Turkish Lira", "alpha_2_code": "TR"},
      "TTD": {"name": "Trinidad and Tobago Dollar", "alpha_2_code": "TT"},
      "TWD": {"name": "Taiwan New Dollar", "alpha_2_code": "TW"},
      "TZS": {"name": "Tanzanian Shilling", "alpha_2_code": "TZ"},
      "UAH": {"name": "Ukrainian Hryvnia", "alpha_2_code": "UA"},
      "UGX": {"name": "Ugandan Shilling", "alpha_2_code": "UG"},
      "USD": {"name": "United States Dollar", "alpha_2_code": "US"},
      "UYU": {"name": "Uruguayan Peso", "alpha_2_code": "UY"},
      "UZS": {"name": "Uzbekistan Som", "alpha_2_code": "UZ"},
      "VND": {"name": "Vietnamese Dong", "alpha_2_code": "VN"},
      "VUV": {"name": "Ni-Vanuatu Vatu", "alpha_2_code": "VU"},
      "WST": {"name": "Samoan Tala", "alpha_2_code": "WS"},
      "XAF": {"name": "CFA Franc BEAC", "alpha_2_code": "CM"},
      "XCD": {"name": "East Caribbean Dollar", "alpha_2_code": "AG"},
      "XDR": {"name": "Special Drawing Rights", "alpha_2_code": "XD"},
      "XOF": {"name": "CFA Franc BCEAO", "alpha_2_code": "BJ"},
      "XPF": {"name": "CFP Franc", "alpha_2_code": "PF"},
      "YER": {"name": "Yemeni Rial", "alpha_2_code": "YE"},
      "ZAR": {"name": "South African Rand", "alpha_2_code": "ZA"},
      "ZMW": {"name": "Zambian Kwacha", "alpha_2_code": "ZM"},
      "ZWL": {"name": "Zimbabwean Dollar", "alpha_2_code": "ZW"}
  }
      
    db.session.query(Currency).delete()
    db.session.commit()
    if db.session.query(Currency).first() is None:
      print('Adding Currency Seeder ... ') 
      
      for code, data in currency_data.items():
        currency = Currency(
            code=code,
            name=data['name'],
            alpha_2_code=data['alpha_2_code']
        )
        db.session.add(currency)
      db.session.commit()
      # url = "{}/currencies?api_key={}".format(current_app.config['FAST_FOREX_API_URL'], current_app.config['FAST_FOREX_API_KEY'])
      # headers = {"accept": "application/json"}
      # response = requests.get(url, headers=headers)
      # if response.status_code == 200:
      #   json_obj = response.json()  
      #   currencies= json_obj['currencies']
      #   for code, name in zip(currencies.keys(), currencies.values()):
      #       currency = Currency(code=code, name=name)
      #       db.session.add(currency)
      #   db.session.commit()
             
      # else:
      #     print(f"Error: {response.status_code} - {response.text}")


    else:
      print('Skipping Currency Seeder ... ')
