from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm
from datetime import date
# db portion
import pyodbc
import warnings
warnings.filterwarnings("ignore")

# put your database info here # connect database here
# and uncomment below line

# conn = pyodbc.connect(
#     "Driver=SQL Server Native Client 11.0;"
#     "Server=MUNEEBS-LAPI;"
#     "Database=ICServices;"
#     "Trusted_Connection=yes;",
#     autocommit=True # added later
# )

# i have to add a check weather product count of that shop is greater then 0 or not
#  if not then do not go to select product page
# Create your views here.


def index(request):
    return render(request, 'mysite/start.html')


def login(request):

    if request.method == 'POST':

        email = str(request.POST['email'])
        passwd = str(request.POST['password'])
        print(f'Id: {email} , Passwd : {passwd}')

        cursor = conn.cursor()
        cursor.execute("select [Email] , [Pass_word] from Buyers")
        buyers_d = cursor.fetchall()
        buyers = []
        for b in buyers_d:
            buyers.append(b)
        cursor.execute("select [Email] , [Pass_word] from Sellers")
        sellers_d = cursor.fetchall()
        sellers = []
        for b in sellers_d:
            sellers.append(b)
        if email and passwd:
            for b in buyers_d:
                if (b[0], b[1]) == (email, passwd):
                    print(' Buyer Login Success !!')
                    cursor = conn.cursor()
                    cursor.execute(
                        "select Buyers.BuyersID from Buyers where Buyers.Email=?", (email))
                    id = cursor.fetchall()
                    id = id[0][0]
                    return render(request, 'mysite/search_shops.html', {'id': id})
            for s in sellers_d:
                if (s[0], s[1]) == (email, passwd):
                    print(' Seller Login Success !!')

                    '''     >>>>>     Here Need to Check if Shop is created or not : 
                            if not login to create shop first else shop dashboard      <<<<<<    '''
                    # cursor.execute("select [_Name] , [Pass_word] from Buyers")
                    # buyers_d = cursor.fetchall()
                    cursor = conn.cursor()
                    cursor.execute(
                        "select Sellers.SellerID from Sellers where Sellers.Email=?", (email))
                    id = cursor.fetchall()
                    id = id[0][0]
                    cursor = conn.cursor()
                    cursor.execute(
                        "SELECT CAST(COUNT(1) AS BIT) AS Expr1 FROM Shops WHERE (SellerID = ?)", (id))
                    check = cursor.fetchall()
                    check = check[0][0]
                    print("Check if Previously Shop Created:", check)
                    if check:
                        # return render(request,'mysite/seller_dashboard.html',{'id':id})
                        cursor = conn.cursor()

                        cursor.execute("""select Products.ProductName,Products.ProductDescrip,Products.Price,Products.PrepTime,Products.ItemsAvailable
                                    from Products where ProductSellerID=?""", (id))
                        data = cursor.fetchall()
                        return render(request, 'mysite/seller_dashboard.html', {'id': id, 'data': data})

                    else:
                        return render(request, 'mysite/create_shop.html', {'id': id})
            messages.info(
                request, "User or Password Not Correct or Not in the record!")
            print("User or Password Not Correct or Not in the record!")
            return redirect('/')
        else:
            messages.info(
                request, "User or Password Not Correct or Not in the record!")
            print("User or Password Not Correct or Not in the record!")
        return redirect('/')
    else:
        return render(request, 'start.html')


def signup(request):

    if request.method == 'POST':

        name = str(request.POST['name'])
        email = str(request.POST['email'])
        passwd = str(request.POST['password'])
        number = str(request.POST['number'])
        usertype = str(request.POST.get('usertype'))

        print(
            f'Name:{name},Email:{email},Passwd:{passwd}\nNo.{number},usertype:{usertype}')

        if usertype != 'None':
            if name and email and passwd and number and usertype:
                cursor = conn.cursor()
                # view used here
                cursor.execute(
                    "SELECT CAST(COUNT(1) AS BIT) AS Expr1 from UsersEmail where (Email=?)", (email))
                check = cursor.fetchall()
                check = check[0][0]
                if check:
                    print("Email Matched With A Previous Record")
                    messages.info(
                        request, "User Already Exits With This Email.")
                    return redirect('/')
                else:
                    # messages.info(request, 'Signup Success !!')
                    print('Signup Success !!')
                    # 1: Buyer
                    # 2: Shop Owner
                    if usertype == '1':
                        cursor = conn.cursor()
                        cursor.execute(
                            "insert into Buyers(_Name,Email,PhoneNumber,Pass_word) values(?,?,?,?);", (name, email, number, passwd))
                        conn.commit()
                        cursor = conn.cursor()
                        cursor.execute(
                            "select Buyers.BuyersID from Buyers where Buyers.Email=?", (email))
                        id = cursor.fetchall()
                        id = id[0][0]
                        return render(request, 'mysite/search_shops.html', {'id': id})
                    if usertype == '2':
                        cursor = conn.cursor()
                        cursor.execute(
                            "insert into Sellers(_Name,Email,PhoneNumber,Pass_word) values(?,?,?,?);", (name, email, number, passwd))
                        conn.commit()
                        cursor = conn.cursor()
                        cursor.execute(
                            "select Sellers.SellerID from Sellers where Sellers.Email=?", (email))
                        id = cursor.fetchall()
                        id = id[0][0]
                        return render(request, 'mysite/create_shop.html', {'id': id})
            else:
                messages.info(
                    request, "Fill All the Inputs with Valid Inputs.")
                print("Invalid Entry Detected :( \nDouble check Inputs.")
                return redirect('/')

        else:
            messages.info(request, "Select User Type Please.")
            print("Invalid Entry Detected :( \nDouble check Inputs.")
            return redirect('/')
    else:
        return render(request, 'mysite/start.html')


def create_shop(request):

    try:
        seller_id = str(request.POST['_id_'])
    except:
        seller_id = None
    if request.method == 'POST':
        seller_id = str(request.POST['_id_'])
        print("_ID_:", seller_id)

        shop_name = str(request.POST['shop_name'])
        institute_name = str(request.POST.get('institute_name'))
        shop_category = str(request.POST.get('shop_category'))

        print(
            f'Shop Name:{shop_name},Institite Name:{institute_name},shop Catogery:{shop_category}')

        if institute_name != 'None' and shop_category != 'None':
            if shop_name and institute_name and shop_category:
                print('Shop Dashboard Loaded')
                cursor = conn.cursor()
                cursor.execute("insert into Shops(SellerID,ShopName,CategoryID,UniversityID) values(?,?,?,?)", (
                    seller_id, shop_name, shop_category, institute_name))
                conn.commit()
                return render(request, 'mysite/seller_dashboard.html', {'id': seller_id})

            else:
                messages.info(
                    request, "Fill All the Inputs with Valid Inputs.")
                print("Invalid Entry Detected :( \nDouble check Inputs.")
                return render(request, 'mysite/create_shop.html', {'id': seller_id})

        else:
            messages.info(request, "Select Items Properly.")
            print("Invalid Entry Detected :( \nDouble check Inputs.")
            return render(request, 'mysite/create_shop.html', {'id': seller_id})
    else:
        return render(request, 'mysite/create_shop.html', {'id': seller_id})


def add_product_btn(request):

    try:
        seller_id = str(request.POST['_id_'])
    except:
        seller_id = None
    if request.method == 'POST':
        seller_id = str(request.POST['_id_'])
        print("_ID_:", seller_id)

        return render(request, 'mysite/add_product.html', {'id': seller_id})

    cursor = conn.cursor()

    cursor.execute("""select Products.ProductName,Products.ProductDescrip,Products.Price,Products.PrepTime,Products.ItemsAvailable
                from Products where ProductSellerID=?""", (seller_id))
    data = cursor.fetchall()
    print('add_product_btn', data)
    return render(request, 'mysite/seller_dashboard.html',  {'id': seller_id, 'data': data})


def add_product(request):

    try:
        seller_id = str(request.POST['_id_'])
    except:
        seller_id = None
    if request.method == 'POST':
        seller_id = str(request.POST['_id_'])

        print("_ID_:", seller_id)
        name = str(request.POST['name'])
        details = str(request.POST['details'])
        price = str(request.POST['price'])
        quantity = str(request.POST['quantity'])
        prep_time = str(request.POST['prep_time'])

        print(
            f'Name:{name},Details:{details},Price:{price}\nQuantity.{quantity},Prep Time:{prep_time}')

        if name and details and price and quantity and prep_time:
            try:
                cursor = conn.cursor()
                cursor.execute("""insert into Products(ProductName,ProductSellerID,Price,PrepTime,ItemsAvailable,ProductDescrip) 
                values(?,?,?,?,?,?)""", (name, seller_id, price, prep_time, quantity, details))
                conn.commit()

                print("Product Added..")
            except:
                messages.info(request, "Error: Check All the Inputs Again.")

                print("Error In Adding Product..")

            cursor = conn.cursor()

            cursor.execute("""select Products.ProductName,Products.ProductDescrip,Products.Price,Products.PrepTime,Products.ItemsAvailable
                        from Products where ProductSellerID=?""", (seller_id))
            data = cursor.fetchall()

            return render(request, 'mysite/seller_dashboard.html', {'id': seller_id, 'data': data})
        else:
            messages.info(request, "Invalid Entry: Check All inputs again.")

            pass

        return render(request, 'mysite/add_product.html', {'id': seller_id})
    cursor = conn.cursor()

    cursor.execute("""select Products.ProductName,Products.ProductDescrip,Products.Price,Products.PrepTime,Products.ItemsAvailable
                from Products where ProductSellerID=?""", (seller_id))
    data = cursor.fetchall()

    return render(request, 'mysite/seller_dashboard.html',  {'id': seller_id, 'data': data})


def edit_product_btn(request):

    try:
        seller_id = str(request.POST['_id_'])
    except:
        seller_id = None
    if request.method == 'POST':
        seller_id = str(request.POST['_id_'])
        print("_ID_:", seller_id)
        cursor = conn.cursor()

        cursor.execute("""select Products.ProductID, Products.ProductName
        from Products
        where ProductSellerID=?""", (seller_id))
        data = cursor.fetchall()
        print("Edt Btn Product Data: ", data)
        if not data:
            messages.info(request, "Error: No Item Exits.")
            print("Error: No Item Exits.")
        else:
            print(data)

            return render(request, 'mysite/select_edit_product.html', {'id': seller_id, 'data': data})
    cursor = conn.cursor()

    cursor.execute("""select Products.ProductName,Products.ProductDescrip,Products.Price,Products.PrepTime,Products.ItemsAvailable
                from Products where ProductSellerID=?""", (seller_id))
    data = cursor.fetchall()
    print('edit_product_btn', data)
    return render(request, 'mysite/seller_dashboard.html',  {'id': seller_id, 'data': data})


def edit_product(request):
    try:
        seller_id = str(request.POST['_id_'])
        cursor = conn.cursor()

        cursor.execute("""select Products.ProductID, Products.ProductName
        from Products
        where ProductSellerID=?""", (seller_id))
        data = cursor.fetchall()
        print(data)
    except:
        seller_id = None
    if request.method == 'POST':
        seller_id = str(request.POST['_id_'])
        product_id = str(request.POST.get('select_product'))
        if product_id:
            print("seller_ID_:", seller_id, "Product", product_id)

            cursor = conn.cursor()

            cursor.execute("""select *
            from Products
            where ProductSellerID=? and ProductID =?""", (seller_id, product_id))
            check = cursor.fetchall()
            check = check[0]
            print("Data for edit:", check)
            # print(check)
            name = check[1]
            price = int(float(check[3]))
            details = check[6]
            quantity = check[5]
            prep_time = check[4]
            print(f"{name},{price},{details},{quantity},{prep_time}")

            if not check:
                messages.info(request, "Error: This Item Not Exit.")

                return render(request, 'mysite/select_edit_product.html', {'id': seller_id, 'data': data})
            else:
                return render(request, 'mysite/edit_product.html', {'id': seller_id, 'product_id': product_id, 'name': name, 'price': price, 'details': details, 'quantity': quantity, 'prep_time': prep_time})

        return render(request, 'mysite/select_edit_product.html', {'id': seller_id, 'data': data})
    return render(request, 'mysite/select_edit_product.html', {'id': seller_id, 'data': data})


def after_edit_product(request):

    try:
        seller_id = str(request.POST['_id_'])
        product_id = str(request.POST['product_id'])
    except:
        seller_id = None
    if request.method == 'POST':
        seller_id = str(request.POST['_id_'])

        print("_ID_:", seller_id)
        name = str(request.POST['name'])
        details = str(request.POST['details'])
        price = str(request.POST['price'])
        quantity = str(request.POST['quantity'])
        prep_time = str(request.POST['prep_time'])

        print(
            f'Name:{name},Details:{details},Price:{price}\nQuantity.{quantity},Prep Time:{prep_time}')

        if name and details and price and quantity and prep_time:
            try:
                cursor = conn.cursor()
                cursor.execute("""UPDATE Products
                SET ProductName =?, Price=?, PrepTime=?, ItemsAvailable = ?,ProductDescrip = ?
                WHERE ProductID = ? and ProductSellerID = ?;""", (name, price, prep_time, quantity, details, product_id, seller_id))
                conn.commit()

                print("Product Updated..")
            except:
                messages.info(request, "Error: Check All the Inputs Again.")

                print("Error In Updating Product..")

            cursor = conn.cursor()

            cursor.execute("""select Products.ProductName,Products.ProductDescrip,Products.Price,Products.PrepTime,Products.ItemsAvailable
                        from Products where ProductSellerID=?""", (seller_id))
            data = cursor.fetchall()

            return render(request, 'mysite/seller_dashboard.html', {'id': seller_id, 'data': data})
        else:
            messages.info(request, "Invalid Entry: Check All inputs again.")

            pass

        return render(request, 'mysite/edit_product.html', {'id': seller_id})
    cursor = conn.cursor()

    cursor.execute("""select Products.ProductName,Products.ProductDescrip,Products.Price,Products.PrepTime,Products.ItemsAvailable
                from Products where ProductSellerID=?""", (seller_id))
    data = cursor.fetchall()

    return render(request, 'mysite/seller_dashboard.html',  {'id': seller_id, 'data': data})


def del_product_btn(request):

    try:
        seller_id = str(request.POST['_id_'])
    except:
        seller_id = None
    if request.method == 'POST':
        seller_id = str(request.POST['_id_'])
        print("_ID_:", seller_id)
        cursor = conn.cursor()

        cursor.execute("""select Products.ProductID, Products.ProductName
        from Products
        where ProductSellerID=?""", (seller_id))
        data = cursor.fetchall()
        print("Del Btn Product Data: ", data)
        if not data:
            messages.info(request, "Error: No Item Exits.")
            print("Error: No Item Exits.")
        else:
            print(data)

            return render(request, 'mysite/delete_product.html', {'id': seller_id, 'data': data})
    cursor = conn.cursor()

    cursor.execute("""select Products.ProductName,Products.ProductDescrip,Products.Price,Products.PrepTime,Products.ItemsAvailable
                from Products where ProductSellerID=?""", (seller_id))
    data = cursor.fetchall()
    print('edit_product_btn', data)
    return render(request, 'mysite/seller_dashboard.html',  {'id': seller_id, 'data': data})


def after_del_product(request):
    try:
        seller_id = str(request.POST['_id_'])
        product_id = str(request.POST.get('select_product'))
        cursor = conn.cursor()

        cursor.execute("""select Products.ProductName,Products.ProductDescrip,Products.Price,Products.PrepTime,Products.ItemsAvailable
                    from Products where ProductSellerID=?""", (seller_id))
        data = cursor.fetchall()
    except:
        seller_id = None
    if request.method == 'POST':
        # seller_id = str(request.POST['_id_'])

        print("_ID_:", seller_id, "Product:", product_id)

        if seller_id and product_id:
            try:
                cursor = conn.cursor()
                cursor.execute("""Delete Products
                WHERE ProductID = ? and ProductSellerID = ?;""", (product_id, seller_id))
                conn.commit()

                print("Product Deleted..")
                messages.info(request, "Product Deleted.")

            except:
                messages.info(request, "Error: Check All the Inputs Again.")

                print("Error In Deleting Product..")

            cursor = conn.cursor()

            cursor.execute("""select Products.ProductName,Products.ProductDescrip,Products.Price,Products.PrepTime,Products.ItemsAvailable
                        from Products where ProductSellerID=?""", (seller_id))
            data = cursor.fetchall()

            return render(request, 'mysite/seller_dashboard.html', {'id': seller_id, 'data': data})
        else:
            messages.info(request, "Invalid Entry: Check All inputs again.")

            return render(request, 'mysite/delete_product.html', {'id': seller_id, 'data': data})

    return render(request, 'mysite/delete_product.html', {'id': seller_id, 'data': data})

    # return render(request, 'mysite/seller_dashboard.html',  {'id': seller_id, 'data': data})


def select_shop(request):
    try:
        buyer_id = str(request.POST['_id_'])
    except:
        buyer_id = None
    if request.method == 'POST':
        buyer_id = str(request.POST['_id_'])
        print("_ID_:", buyer_id)

        institute_id = str(request.POST.get('institute_name'))
        shop_category = str(request.POST.get('shop_category'))
        print(f'Institite Name:{institute_id},shop Catogery:{shop_category}')

        if institute_id != 'None' and shop_category != 'None':
            if institute_id and shop_category:
                print('Select Shop Loaded')
                cursor = conn.cursor()
                cursor.execute("select * from Shops where CategoryID = ? and UniversityID = ?", (
                    shop_category, institute_id))
                data = cursor.fetchall()
                print(data)
                if not data:
                    messages.info(request, "No Shop Found!")
                    print("No Shop Found :( .")
                    return render(request, 'mysite/search_shops.html', {'id': buyer_id})
                return render(request, 'mysite/select_shop.html', {'id': buyer_id, 'institute_id': institute_id, 'shop_category': shop_category, 'data': data})

            else:
                messages.info(
                    request, "Invalid Inputs!")
                print("Invalid Entry Detected :( \nDouble check Inputs.")
                return render(request, 'mysite/search_shops.html', {'id': buyer_id})

        else:
            # messages.info(request, "Select Items Properly.")
            print("Invalid Entry Detected :( \nDouble check Inputs.")
            return render(request, 'mysite/search_shops.html', {'id': buyer_id})
    else:
        return render(request, 'mysite/search_shops.html', {'id': buyer_id})


def buyer_dashboard(request):
    try:
        buyer_id = str(request.POST['_id_'])
        institute_id = str(request.POST['institute_id'])
        shop_category = str(request.POST['shop_category'])
        print(f'Institite Name:{institute_id},shop Catogery:{shop_category}')
        print('Select Shop Loaded')
        cursor = conn.cursor()
        cursor.execute("select * from Shops where CategoryID = ? and UniversityID = ?", (
            shop_category, institute_id))
        data = cursor.fetchall()
        print(data)
    except:
        buyer_id = None
    if request.method == 'POST':
        buyer_id = str(request.POST['_id_'])
        print("Buyer_ID:", buyer_id)

        shop_id = str(request.POST.get('shop_id'))

        print(f'ShopID:{shop_id}')

        if shop_id:
            print('Buyer Dash Loaded')
            cursor = conn.cursor()
            cursor.execute("select Products.ProductID, Products.ProductName,Products.ProductDescrip,Products.Price,Products.PrepTime,Products.ItemsAvailable from Products where ProductSellerID = ?", (
                shop_id))
            data = cursor.fetchall()
            print(data)
            if data:
                return render(request, 'mysite/buyer_dashboard.html', {'id': buyer_id, 'data': data, 'shop_id': shop_id})
            else:
                messages.info(request, "No Shop Found!")
                print("No Shop Found :( .")
                return render(request, 'mysite/search_shops.html', {'id': buyer_id})

        else:
            print("Invalid Entry Detected :( \nDouble check Inputs.")
            return render(request, 'mysite/select_shop.html', {'id': buyer_id, 'data': data, 'institute_id': institute_id, 'shop_category': shop_category})

    else:
        return render(request, 'mysite/select_shop.html', {'id': buyer_id, 'data': data, 'institute_id': institute_id, 'shop_category': shop_category})


def cart(request):
    try:
        buyer_id = str(request.POST['_id_'])
        shop_id = str(request.POST['shop_id'])
        cursor = conn.cursor()
        cursor.execute("select Products.ProductID, Products.ProductName,Products.ProductDescrip,Products.Price,Products.PrepTime,Products.ItemsAvailable from Products where ProductSellerID = ?", (shop_id))
        fdata = cursor.fetchall()
    except:
        buyer_id = None
    if request.method == 'POST':
        buyer_id = str(request.POST['_id_'])
        print("_ID_:", buyer_id)
        shop_id = str(request.POST['shop_id'])
        cursor = conn.cursor()
        cursor.execute("select Products.ProductID, Products.ProductName,Products.ProductDescrip,Products.Price,Products.PrepTime,Products.ItemsAvailable from Products where ProductSellerID = ?", (shop_id))
        data = cursor.fetchall()

        print(f'Shop ID:{shop_id}')

        if shop_id != 'None':
            if shop_id:
                print('Cart Loaded')
                cursor = conn.cursor()
                cursor.execute("select Products.ProductID  from Products where ProductSellerID = ?", (
                    shop_id))
                data = cursor.fetchall()
                print(data)
                prod_list = []
                for x in data:
                    prod_list.append(x[0])

                print(prod_list)
                if not prod_list:
                    messages.info(request, "No Item Added!")
                    print("No Shop Found :( .")
                    return render(request, 'mysite/buyer_dashboard.html', {'id': buyer_id, 'data': fdata})
                counts = []
                for x in prod_list:
                    counts.append(int(str(request.POST[f'{x}'])))
                print(counts)
                prod_count_lst = []
                prod_list_final = []
                for i in range(len(prod_list)):
                    if counts[i] > 0:
                        prod_count_lst.append(prod_list[i])
                        prod_count_lst.append(counts[i])
                        #
                        prod_list_final.append(prod_list[i])

                # converting prod count lst to dict
                it = iter(prod_count_lst)
                items_dct = dict(zip(it, it))
                print(prod_count_lst)
                print('DCT:', items_dct)

                lst = prod_list_final
                cursor.execute(""" Select Products.ProductID , Products.Price From Products where ProductID in ({}) """.format(
                    ','.join("?"*len(lst))), lst)
                rows = cursor.fetchall()
                print('Final :', rows)
                total_price = 0
                final_insert_orderItems_lst = []  # prodID , price , quantity
                for i in rows:
                    final_insert_orderItems_lst.append(
                        [i[0], i[1], items_dct[i[0]]])
                    total_price += int(i[1])*int(items_dct[i[0]])
                print("final_insert_orderItems_lst:",
                      final_insert_orderItems_lst)
                print("Total Price:", total_price)
                today = date.today()
                # creating order in database :
                cursor = conn.cursor()
                cursor.execute(
                    """insert into Orders(BuyersID,OrderDate,TotalAmount) values (?,?,?)""", (buyer_id, today, total_price))
                conn.commit()
                # getting id of that inserted order
                cursor = conn.cursor()
                cursor.execute(
                    "select OrderID  from Orders where BuyersID=? AND OrderDate = ? AND TotalAmount = ?", (buyer_id, today, total_price))
                data = cursor.fetchall()
                order_id = data[0][0]
                print("Order ID:", order_id)

                for item in final_insert_orderItems_lst:
                    cursor = conn.cursor()
                    cursor.execute("""insert into OrderItem(ItemID,OrderID,ProductSellerID,UnitPrice,Quantity) 
                    values(?,?,?,?,?)""", (item[0], order_id, shop_id, item[1], item[2]))
                    conn.commit()

                cursor = conn.cursor()
                cursor.execute("""Select ROW_NUMBER() over(order by ItemID) as Item# ,Products.ProductName,UnitPrice , Quantity , UnitPrice*Quantity 
                as totalItemPrice
                From OrderItem join Products on OrderItem.ItemID=Products.ProductID
                where OrderID = ?""", (order_id))
                data = cursor.fetchall()

                return render(request, 'mysite/cart.html', {'id': buyer_id, 'data': data, 'total_price': total_price})

            else:
                messages.info(
                    request, "InValid Inputs!")
                print("Invalid Entry Detected :( \nDouble check Inputs.")
                return render(request, 'mysite/buyer_dashboard.html', {'id': buyer_id, 'data': fdata})

        else:
            messages.info(request, "Select Items Properly.")
            print("Invalid Entry Detected :( \nDouble check Inputs.")
            return render(request, 'mysite/buyer_dashboard.html', {'id': buyer_id, 'data': fdata})
    else:
        return render(request, 'mysite/buyer_dashboard.html', {'id': buyer_id, 'data': fdata})
