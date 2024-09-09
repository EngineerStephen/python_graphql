import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType
from models import Order as OrderModel, db

class Order(SQLAlchemyObjectType):
    class Meta:
        model = OrderModel

class Query(graphene.ObjectType):
    orders = graphene.List(Order)
    search_orders = graphene.List(Order, name=graphene.String(), customer=graphene.String(), order_date=graphene.DateTime())

    def resolve_orders(self, info):
        return db.session.execute(db.select(OrderModel)).scalars()
    
    def resolve_search_orders(self, info, name=None, customer=None, order_date=None):
        query = db.select(OrderModel)
        if name:
            query = query.where(OrderModel.name.ilike(f'%{name}%'))
        if customer:
            query = query.where(OrderModel.customer.ilike(f'%{customer}%'))
        if order_date:
            query = query.where(OrderModel.order_date == order_date)
        results = db.session.execute(query).scalars().all()
        return results


class AddOrder(graphene.Mutation):
    class Arguments: 
        name = graphene.String(required=True)
        customer = graphene.String(required=True)
        order_date = graphene.DateTime(required=True)
    
    order = graphene.Field(Order)

    def mutate(self, info, name, customer, order_date): 
        order = OrderModel(name=name, customer=customer, order_date=order_date)
        db.session.add(order)
        db.session.commit() 

        db.session.refresh(order)
        return AddOrder(order=order)

class UpdateOrder(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        name = graphene.String(required=False)
        customer = graphene.String(required=False)
        order_date = graphene.DateTime(required=False)
    order = graphene.Field(Order)

    def mutate(self, info, id, name=None, customer=None, order_date=None):
        order = db.session.get(OrderModel, id)
        if not order:
            return None
        if name:
            order.name = name
        if customer:
            order.customer = customer
        if order_date:
            order.order_date = order_date

        db.session.add(order)
        db.session.commit()
        return UpdateOrder(order=order)
    
class DeleteOrder(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
    
    order = graphene.Field(Order)

    def mutate(self, info, id):
        order = db.session.get(OrderModel, id)
        if order:
            db.session.delete(order)
            db.session.commit()
        else:
            return None
        
        return DeleteOrder(order=order)

class Mutation(graphene.ObjectType):
    create_order = AddOrder.Field()
    update_order = UpdateOrder.Field()
    delete_order = DeleteOrder.Field()
