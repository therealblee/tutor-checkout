import flask
import os
import mongo
import stripe

stripe.api = os.environ['STRIPE_API_KEY']

class Customer(stripe.Customer):

	def addCard(self, **kwargs):
		card = self.sources.create(
			source=kwargs,
		)

		return card

	def checkout(self, cart=None):
		'''Checkout and return order.'''
		cart = cart or Cart.get()
		items = cart.itemsToDict()

		try:
			order = stripe.Order.create(
				currency='usd',
				customer=self.id,
				email=self.email,
				items=items,
			)

			order.pay(customer=self.id)

			cart.empty()

			return order
		except stripe.error.CardError, e:
			print e.message
		except Exception, e:
			print e.message

		return None

	@classmethod
	def retrieve(cls, stripeCustomerId):
		customer = super(stripe.Customer, cls).retrieve(stripeCustomerId, expand=['default_source'])
		if customer:
			customer.phone = customer.metadata.phone

			student = Student.fromCustomerMetadata(customer.metadata)
			customer.student = student

			return customer
		else:
			return None

class Card(stripe.Card):

	@classmethod
	def retrieve(cls, stripeCardId):
		stripeCard = super(stripe.Card, cls).retrieve(stripeCardId)
		if stripeCard:
			billingAddress = Address.fromStripeCard(stripeCard)
			stripeCard.billingAddress = billingAddress

			return stripeCard
		else:
			return None

class Address(object):

	def __init__(self, streetLine1, streetLine2, city, state, zipCode):
		self.streetLine1 = streetLine1
		self.streetLine2 = streetLine2
		self.city = city
		self.state = state
		self.zipCode = zipCode

	@classmethod
	def fromStripeCard(cls, stripeCard):
	 	return Address(
			stripeCard.address_line1,
			stripeCard.address_line2,
			stripeCard.address_city,
			stripeCard.address_state,
			stripeCard.address_zip,
		)

class Cart(object):

	def __init__(self):
		self.items = []
		self.total = 0.0

	@classmethod
	def get(cls):
		return flask.session.get('cart') or Cart()

	def addProduct(self, product):
		self.addProducts(product, 1)

	def addProducts(self, product, quantity):
		cartItem = self.getCartItemForProduct(product)
		if cartItem:
			cartItem.quantity += quantity
		else:
			cartItem = CartItem(product, quantity)
			self.items.append(cartItem)

		self.updateTotal()

	def addItem(self, item):
		cartItem = self.getCartItemForProduct(item.product)
		if cartItem:
			cartItem.quantity += item.quantity
		else:
			self.items.append(item)

		self.updateTotal()

	def getCartItemForProduct(self, product):
		# group by product name, which is our product id
		for item in self.items:
			if item.product.name == product.name:
				return item

		return None

	def removeProduct(self, product):
		cartItem = self.getCartItemForProduct(product)
		if cartItem and cartItem in self.items:
			self.items.remove(cartItem)
			self.updateTotal()

	def updateProductQuantity(self, product, quantity):
		cartItem = self.getCartItemForProduct(product)
		if quantity > 0 and cartItem:
			cartItem.quantity = quantity
		else:
			if cartItem in self.items:
				self.items.remove(cartItem)

		self.updateTotal()

	def updateTotal(self):
		self.total = 0.0
		for item in self.items:
			self.total += item.getItemTotal()

	def empty(self):
		self.items = []
		self.total = 0.0

	def itemsToDict(self):
		return [item.toDict() for item in self.items]

	def __eq__(self, other):
		return set(self.items) == set(other.items) and self.total == other.total

class CartItem(object):

	__hash__ = None

	def __init__(self, product, quantity):
		self.product = product
		self.quantity = quantity

	def getItemTotal(self):
		return self.product.price * self.quantity

	def toDict(self):
		return {
			'amount': self.getItemTotal(),
			'currency': 'usd',
			'description': self.product.description,
			'parent': self.product.sku,
			'quantity': self.quantity,
			'type': 'sku',
		}

	def __eq__(self, other):
		return isinstance(self, CartItem) and \
			self.product == other.product and \
			self.quantity == other.quantity

class Product(object):

	def __init__(self, name, description, price, sku=None):
		self.sku = sku
		self.name = name
		self.description = description
		self.price = price

	@classmethod
	def fromDict(cls, productDict):
		return Product(
			productDict.get('sku'),
			productDict.get('name'),
			productDict.get('description'),
			productDict.get('price'),
		)

	def __eq__(self, other):
		return isinstance(self, Product) and \
			self.sku == other.sku and \
			self.name == other.name and \
			self.description == other.description and \
			self.price == other.price

class Student(object):

	def __init__(self, name, grade, subject, goals):
		self.name = name
		self.grade = grade
		self.subject = subject
		self.goals = goals

	@classmethod
	def fromCustomerMetadata(cls, metadata):
		return Student(
			metadata.studentName,
			metadata.grade,
			metadata.subject,
			metadata.goals,
		)
