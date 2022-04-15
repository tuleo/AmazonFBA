"""
Created on Fri Mar  4 16:42:24 2022

@author: F999181
"""
import streamlit as st
import pandas as pd
import numpy as np
from typing import List, Optional, Type
import plotly.graph_objects as go
import json
import warnings

class TooHighBSR(Exception):
    pass

class NotUniqueCategory(Exception):
    pass

class TooCompetitiveNiech(Exception):
    pass

class Product:
    """
    Class that represents an Amazon Product

    Parameters:
        url: amazon list url till the ASIN
        keywords: keywords to search the 
        category: product Amazon main category
        price: unit price
        BSR: best seller rank
        reviews: number of reviews
        monthly_sales: amount of monthly sales
        estimated_sourcing_cost: cost to source the product from the factory
                                 unit costs plus shipping
        fba_fee: fee to sell on Amazon FBA service
        referal_fee: comission per sell (usually 15% of the unit price)
    """
    def __init__(self, 
                 url:str,
                 keywords:List[str],
                 category:str,
                 price:float,
                 BSR:int,
                 reviews:int,
                 monthly_sales:int,
                 estimated_sourcing_cost:float,
                 fba_fee:float,
                 referal_fee:float
                 ):
        #Recommended categories with suitable BSR ranges
        BSR_ranges = {
                      'baby':(100, 7500),
                      'beauty':(100, 19000),
                      'office':(100, 14000),
                      'pet supplies':(100, 14000),
                      'sports and outdoors':(100, 17000),
                      'home and kitchen':(100, 24000),
                      'kitchen and dining':(100, 17000),
                      'patio, lawn and garden':(100, 8500),
                      'toys and games':(100, 17000),
                     }
    
        self.url = url
        self.keywords = keywords
        self.category = category
        if self.category not in BSR_ranges.keys():
            raise Exception("Product Category not known.")
        self.price = price
        #Check range of prices
        if price < 19.99 or price > 50.0:
            warnings.warn("Product price not in te desired range. 19.99 < price > 50.00")
            st.warning("Product price not in te desired range. 19.99 < price > 50.00")
        self.BSR = BSR
        #Check if the product is in the desired competitive range
        if (self.BSR > BSR_ranges[self.category][1]):
            raise TooHighBSR("Product not in the competing BSR ranges.")
        self.reviews = reviews
        self.monthly_sales = monthly_sales
        self.monthly_revenue = monthly_sales*price
        self.estimated_sourcing_cost = estimated_sourcing_cost
        self.fba_fee = fba_fee 
        self.referal_fee = referal_fee
        self.vat = 0.75*0.23*self.price
        jungle_scout_fee = 50 #monthly jungle scout subscription
        ppc_fee = 500  #money paid in pay-per-click adds
        self.profit = self.price - self.estimated_sourcing_cost - self.fba_fee - self.referal_fee - self.vat
        self.monthly_profit = self.profit * self.monthly_sales - jungle_scout_fee - ppc_fee
        #Between 15 and 20 percent is considered an healthy profit margin
        self.profit_margin = self.profit/self.price

    @classmethod
    def init_from_dict(cls, product_parameters:dict):
        return cls(**product_parameters)

    def __str__(self):
        print(f"""
              Category: {self.category}
              Price: {self.price}
              Profit Margin: {self.profit_margin}
              """)

    def price_vs_monthly_revenue(self, 
                                 price_range:Optional[Type[np.array]]=np.arange(5, 100, 1)) -> Type[go.Figure]:
        """
        Graph of the unit price vs monthly revenue

        Parameters: 
            price_range: range for the product unit price
        """
        profit_range = np.array([price-self.estimated_sourcing_cost-self.fba_fee-self.referal_fee 
                                 for price in price_range])
        monthly_revenue_range = np.array([profit*self.monthly_sales 
                                         for profit in profit_range])
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=price_range, 
                                 y=monthly_revenue_range,
                                 mode='lines+markers',))
        return fig

    def break_even_price(self) -> float:
        """
        Calculate the breakeven price 

        Parameters:
            break_even_price: price that leads to zero profit
        """
        break_even_price = self.estimated_sourcing_cost + self.fba_fee + self.referal_fee + self.vat
        return break_even_price

    def into_dict(self) -> dict:
        """
        Convert the Product instance into a dictionary

        Parameters:
            product_parameters: parameters of the Product instance
        """
        product_parameters = {
                              'url':self.url,
                              'keywords':self.keywords,
                              'category':self.category,
                              'price':self.price,
                              'BSR':self.BSR,
                              'reviews':self.reviews,
                              'monthly_sales':self.monthly_sales,
                              'estimated_sourcing_cost':self.estimated_sourcing_cost,
                              'fba_fee':self.fba_fee,
                              'referal_fee':self.referal_fee,
                             }
        return product_parameters


class Products:
    """
    Representation of a niech (a collection of products)

    Parameters:
        products: a list of Product instances
    """
    def __init__(self,  
                 products:List[Type[Product]]):
        self.products = products
        if products:
            self.update_state()
        else:
            self.number_products : int = 0
            self.primary_product : Type[Product] = None
            self.competitors : List[Type[Product]]= []
            self.category = ''
            
    @classmethod
    def init_from_json(cls, path:str,):
        """
        Initialization from a .json file

        Parameters:
            path: path of the .json file
        """
        with open(path, 'r') as f:
            products_dict = json.load(f)
        products = [Product.init_from_dict(product_parameters) for product_parameters in products_dict]
        return cls(products)

    @classmethod
    def init_from_list_dict(cls, products_dict:List[dict]):
        """
        Initialization from a list of product parameters

        Parameters:
            products_dict: list of product parameters
        """
        products = [Product.init_from_dict(product_parameters) for product_parameters in products_dict]
        return cls(products)

    def into_list_dict(self) -> List[dict]:
        """
        Convert a products.Products instance into a list of product parameters

        Returns:
            products_dict: list of product parameters
        """
        products_dict = []
        for product in self.products:
            product_parameters = product.into_dict()
            products_dict.append(product_parameters)
        return products_dict

    def into_json(self, path:str) -> None:
        """
        Converts a product.Products into a .json file

        Parameters:
            path: path of the .json file
        """
        products = self.into_list_dict()
        with open(path, 'w') as f:
            json.dump(products, f)

    @staticmethod
    def unique(list_:list) -> list:
        """
        Returns a list with all the unique entries
        """ 
        list_set = set(list_)
        unique_list = (list(list_set))
        return unique_list

    def add(self, product:Type[Product]) -> None:
        """
        Add a product

        Parameters:
            product: products.Product instance
        """
        self.products.append(product)
        categories = [product.category for product in self.products]
        unique_categories = Products.unique(categories)
        if len(unique_categories) > 1:
            raise NotUniqueCategory("Not all products belong to the same category.")
        self.category = unique_categories[0]
        self.update_state()

    def update_state(self):
        """
        Update the state of the products.Products instance
        """
        reviews = [product.reviews for product in self.products]
        self.category = self.products[0].category
        if min(reviews) > 1000 and len(reviews) >= 3:
            raise TooCompetitiveNiech("Too competitive Niech. Minimum number of reviews higher than 1000.")
        self.number_products = len(self.products)
        #Sort the products by BSR
        sorted_products = sorted(self.products, key=lambda x: x.BSR, reverse=False)
        self.products = sorted_products
        self.competitors = self.products[1:]
        self.primary_product = self.products[0]
        
    def dataframe(self) -> Type[pd.DataFrame]:
        """
        Convert the products.Products instance into an explainable dataframe

        Returns:
            df: products dataframe
        """
        dict_ = {'URL': [product.url for product in self.products],
                 'Keywords': [product.keywords for product in self.products],
                 'BSR': [product.BSR for product in self.products],
                 'Reviews': [product.reviews for product in self.products],
                 'Monthly Revenue': [product.monthly_revenue for product in self.products],
                 'Monthly Sales': [product.monthly_sales for product in self.products],
                 'Price': [product.price for product in self.products],
                 'Cost': [product.estimated_sourcing_cost for product in self.products],
                 'Profit': [product.profit for product in self.products],
                 'Profit Margin': [product.profit_margin for product in self.products]}
        
        df = pd.DataFrame(dict_)
        df = df.sort_values(by='BSR', ascending=True)
        return df

    def hypothesis_product(self) -> Type[Product]:
        """
        Create a representative product of the niech

        Returns:
            hypothesis_product: representation of the niech in a single product
        """
        hypothesis_product = Product(
                                     url='', 
                                     keywords=[''], 
                                     category=self.category,
                                     price=np.array([product.price for product in self.products]).mean(),
                                     BSR=np.array([product.BSR for product in self.products]).mean(),
                                     reviews=np.array([product.reviews for product in self.products]).mean(),
                                     monthly_sales=np.array([product.monthly_sales for product in self.products]).mean(),
                                     estimated_sourcing_cost=np.array([product.estimated_sourcing_cost for product in self.products]).mean(),
                                     fba_fee=np.array([product.fba_fee for product in self.products]).mean(),
                                     referal_fee=np.array([product.referal_fee for product in self.products]).mean(),
                                    )
        return hypothesis_product

    

    
