import pymongo

class Model(object):

	__tablename__ = None
	__dbname__ = None
	fields = []

	def __init__(self, *args, **kwargs):
		for field in self.fields:
			if field in kwargs:
				setattr(self, field, kwargs[field])
			else:
				setattr(self, field, None)

	@classmethod
	def getAll(cls):
		return [cls(**mongo_object) for mongo_object in cls.get_collection().find()]

	@classmethod
	def deleteById(cls, id):
		cls.get_collection().delete_one({'_id': ObjectId(id)})

	@classmethod
	def insertOne(cls, **kwargs):
		cls.get_collection().insert_one(kwargs)

	@classmethod
	def findById(cls, id):
		return cls.find_one({'_id': ObjectId(id)})

	@classmethod
	def findOne(cls, query):
		document = cls.get_collection().find_one(query)
		if document:
			return cls(**document)
		else:
			return None

	@classmethod
	def find(cls, query, sort=None):
		documents = cls.get_collection().find(query, sort=sort)
		if documents:
			return [cls(**document) for document in documents]
		else:
			return []

	@classmethod
	def updateById(cls, id, query=None, **kwargs):
		cls.get_collection().update_one(
			{'_id': ObjectId(id)},
			{'$set': { kwargs, query or {} }}
		)

	@classmethod
	def getCollection(cls):
		client = pymongo.MongoClient()
		mongoDb = client[cls.__dbname__]
		return mongoDb[cls.__tablename__]
