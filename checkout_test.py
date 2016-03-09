import os
import stripe
import unittest

from checkout import Customer, Cart, CartItem, Product

stripe.api_key = os.environ['STRIPE_API_KEY']
MY_CUSTOMER_ID = os.environ['TEST_CUSTOMER_ID']

class CustomerTest(unittest.TestCase):

	def setUp(self):
		self.customer = Customer.retrieve(MY_CUSTOMER_ID)

	def testCheckout(self):
		product = Product('louis ck', 'funny guy', 10000, 'sku_83GNftr3jrpP5f')

		# set the cart that customer will checkout
		cart = Cart()
		cart.addProducts(product, 5)

		order = self.customer.checkout(cart=cart)
		self.assertEqual(order.amount, 50000.0)

	def testRetrieve(self):
		'''
			Assume all fields from Python Stripe API documentation exist
			and are correct. Just check value of student attribute.
		'''
		self.assertEqual(self.customer.phone, '4444444444')

		student = self.customer.student
		self.assertEqual(student.name, 'Brian Lee')
		self.assertEqual(student.grade, '10')
		self.assertEqual(student.subject, 'Freestyling')
		self.assertEqual(student.goals, 'Droppin bars like Eminem in 8 Mile')

class CartTest(unittest.TestCase):

	def setUp(self):
		self.cart = Cart()
		self.products = [
			Product('bars', 'klondike', 5),
			Product('pitbull', 'mr 305', 10),
			Product('big data', 'buzzword', 1),
		]

	def testUpdateTotal(self):
		self.cart.updateTotal()
		self.assertEqual(self.cart.total, 0.0)

		cartItem = CartItem(self.products[0], 3)
		self.cart.items = [cartItem]
		self.cart.updateTotal()
		self.assertEqual(self.cart.total, 15.0)

		cartItem2 = CartItem(self.products[1], 4)
		self.cart.items.append(cartItem2)
		self.cart.updateTotal()
		self.assertEqual(self.cart.total, 55.0)

		self.cart.items.append(cartItem)
		self.cart.updateTotal()
		self.assertEqual(self.cart.total, 70.0)

	def testAddProducts(self):
		self.cart.addProducts(self.products[0], 3)

		cartItem = CartItem(self.products[0], 3)
		self.assertListEqual(self.cart.items, [cartItem])
		self.assertEqual(self.cart.total, 15.0)

		self.cart.addProducts(self.products[0], 5)

		cartItem = CartItem(self.products[0], 8)
		self.assertListEqual(self.cart.items, [cartItem])
		self.assertEqual(self.cart.total, 40.0)

		self.cart.addProducts(self.products[1], 2)
		cartItem2 = CartItem(self.products[1], 2)
		self.assertListEqual(self.cart.items, [cartItem, cartItem2])
		self.assertEqual(self.cart.total, 60.0)

	def testAddItem(self):
		cartItem = CartItem(self.products[2], 2)
		self.cart.addItem(cartItem)
		
		self.assertListEqual(self.cart.items, [cartItem])
		self.assertEqual(self.cart.total, 2.0)

		cartItem2 = CartItem(self.products[1], 2)
		self.cart.addItem(cartItem2)

		self.assertListEqual(self.cart.items, [cartItem, cartItem2])
		self.assertEqual(self.cart.total, 22.0)

		cartItem = CartItem(self.products[2], 2)
		self.cart.addItem(cartItem)

		updatedCartItem = CartItem(self.products[2], 4)
		self.assertListEqual(self.cart.items, [updatedCartItem, cartItem2])
		self.assertEqual(self.cart.total, 24.0)

	def testRemoveProduct(self):
		self.cart.removeProduct(self.products[0])
		self.assertEqual(len(self.cart.items), 0)

		self.cart.addProduct(self.products[0])
		self.cart.removeProduct(self.products[1])
		self.assertEqual(len(self.cart.items), 1)
		self.cart.removeProduct(self.products[0])
		self.assertEqual(len(self.cart.items), 0)

		self.cart.addProduct(self.products[0])
		self.cart.addProduct(self.products[1])

		self.cart.removeProduct(self.products[1])
		self.assertEqual(self.cart.items[0].product.name, 'bars')
		self.assertEqual(len(self.cart.items), 1)

	def testUpdateProductQuantity(self):
		self.cart.updateProductQuantity(self.products[1], 0)
		self.assertListEqual(self.cart.items, [])

		cartItem = CartItem(self.products[2], 2)
		self.cart.addItem(cartItem)

		cartItem = CartItem(self.products[2], 5)
		self.cart.updateProductQuantity(self.products[2], 5)
		self.assertListEqual(self.cart.items, [cartItem])
		self.assertEqual(self.cart.total, 5.0)

		cartItem2 = CartItem(self.products[1], 3)
		self.cart.addItem(cartItem2)

		self.assertListEqual(self.cart.items, [cartItem, cartItem2])
		self.cart.updateProductQuantity(self.products[1], 0)
		self.assertListEqual(self.cart.items, [cartItem])

		self.cart.updateProductQuantity(self.products[2], -1)
		self.assertListEqual(self.cart.items, [])

	def testEmpty(self):
		self.cart.empty()
		self.assertEqual(self.cart, Cart())

		cartItem = CartItem(self.products[2], 2)
		self.cart.addItem(cartItem)
		
		self.cart.empty()
		self.assertEqual(self.cart, Cart())

class CartItemTest(unittest.TestCase):

	def setUp(self):
		product = Product('trump', 'joke', 0.01)
		self.cartItem = CartItem(product, 5)

	def testGetItemTotal(self):
		self.assertEqual(self.cartItem.getItemTotal(), 0.05)

if __name__ == '__main__':
	unittest.main()