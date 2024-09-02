import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType
from models import Bakery as BakeryModel, db

class Bakery(SQLAlchemyObjectType):
    class Meta:
        model = BakeryModel

class Query(graphene.ObjectType):
    bakeries = graphene.List(Bakery)
    search_bakeries = graphene.List(Bakery, name=graphene.String(), customer=graphene.String(), order_date=graphene.DateTime())

    def resolve_bakeries(self, info):
        return db.session.execute(db.select(BakeryModel)).scalars()
    
    def resolve_search_bakeries(self, info, name=None, customer=None, order_date=None):
        query = db.select(BakeryModel)
        if name:
            query = query.where(BakeryModel.name.ilike(f'%{name}%'))
        if customer:
            query = query.where(BakeryModel.customer.ilike(f'%{customer}%'))
        if order_date:
            query = query.where(BakeryModel.order_date == order_date)
        results = db.session.execute(query).scalars().all()
        return results


class AddBakery(graphene.Mutation): 
    class Arguments: 
        name = graphene.String(required=True)
        customer = graphene.String(required=True)
        order_date = graphene.DateTime(required=True)
    
    bakery = graphene.Field(Bakery)

    def mutate(self, info, name, customer, order_date): 
        bakery = BakeryModel(name=name, customer=customer, order_date=order_date)
        db.session.add(bakery)
        db.session.commit() 

        db.session.refresh(bakery)
        return AddBakery(bakery=bakery)
    
class UpdateBakery(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        name = graphene.String(required=False)
        customer = graphene.String(required=False)
        order_date = graphene.DateTime(required=False)

    bakery = graphene.Field(Bakery)

    def mutate(self, info, id, name=None, customer=None, order_date=None):
        bakery = db.session.get(BakeryModel, id)
        if not bakery:
            return None
        if name:
            bakery.name = name
        if customer:
            bakery.customer = customer
        if order_date:
            bakery.order_date = order_date

        db.session.add(bakery)
        db.session.commit()
        return UpdateBakery(bakery=bakery)
    
class DeleteBakery(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
    
    bakery = graphene.Field(Bakery)

    def mutate(self, info, id):
        bakery = db.session.get(BakeryModel, id)
        if bakery:
            db.session.delete(bakery)
            db.session.commit()
        else:
            return None
        
        return DeleteBakery(bakery=bakery)

class Mutation(graphene.ObjectType):
    create_bakery = AddBakery.Field()
    update_bakery = UpdateBakery.Field()
    delete_bakery = DeleteBakery.Field()
