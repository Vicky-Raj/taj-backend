import csv
import pandas as pd
def write_order_csv(details_dict):
    with open('orderlist.csv','w',newline='') as csv_file:
        field_names=['InvoiceNo','CustomerId','CustomerName','CustomerNumber','TotalAmount']
        writer=csv.DictWriter(csv_file,fieldnames=field_names)
        writer.writeheader()
        writer.writerow(details_dict)
        print("Written Successfully")

def write_daily_csv(details_dict):
     pass


      
