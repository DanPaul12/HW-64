import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType
from models import Product as ProductModel, db
from sqlalchemy.orm import Session

class Product(SQLAlchemyObjectType):
    class Meta:
        model = ProductModel

class Query(graphene.ObjectType):
    products = graphene.List(Product)

    def resolve_products(self, info):
        return db.session.execute(db.select(ProductModel)).scalars()
    
class AddProduct(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        flavor = graphene.String(required=True)
        price = graphene.Float(required=True)
    
    product = graphene.Field(Product)

    def mutate(self, info, name, flavor, price):
        with Session(db.engine) as session:
            with session.begin():
                product = ProductModel(name=name, flavor=flavor, price=price)
                session.add(product)
            
            session.refresh(product)
            return AddProduct(product=product)
        
class UpdateProduct(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        name = graphene.String(required=True)
        flavor = graphene.String(required=True)
        price = graphene.Float(required=True)

    product = graphene.Field(Product)

    def mutate(self, info, id, name, flavor, price):
        with Session(db.engine) as session:
            with session.begin():
                product = session.execute(db.select(ProductModel).where(ProductModel.id == id)).scalars().first()
                if product:
                    product.name = name
                    product.flavor = flavor
                    product.price = price
                else:
                    return None
            session.refresh(product)
            return UpdateProduct(product=product)
        
class DeleteProduct(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    product = graphene.Field(Product)

    def mutate(self, info, id):
        with Session(db.engine) as session:
            with session.begin():
                product = session.execute(db.select(ProductModel).where(ProductModel.id == id)).scalars().first()
                if product:
                    session.delete(product)
                else:
                    return None
            session.refresh(product)
            return DeleteProduct(product=product)


        
class Mutation(graphene.ObjectType):
    create_product = AddProduct.Field()
    update_product = UpdateProduct.Field()
    delete_product = DeleteProduct.Field()