from flask import (
        render_template, #Flask
        request, redirect, jsonify 
    )
#from flask_sqlalchemy import SQLAlchemy
#from flask_marshmallow import Marshmallow
from flask_restful import Resource #Api, 
from datetime import datetime
'''from project(local), we are importing these packages / file '''
from config import (
        app, db, ma, api
    )


class Todolist(db.Model):
    __tablename__ = 'todo'
    id = db.Column(db.Integer, primary_key=True)                            # ID (Internal column for the table)
    name = db.Column(db.String(100), nullable=False, unique=True)                        # Name for the Task
    created_at = db.Column(db.DateTime, nullable=False,                     # Start Date for the Task
                           default=datetime.utcnow)
    target_at = db.Column(db.String(10), nullable=False)                    # Target Date for completing the Task       
    
    def __init__(self, name, target_at):
       self.name = name
       self.target_at = target_at
 
    def save(self):
       db.session.add(self)
       db.session.commit()

    def __repr__(self):
        return "<Todolist(name='%s', target_at='%s')>" % (self.name, self.target_at)


##fields to expose to our users
class TodolistSchema(ma.Schema):
    class Meta:
        fields = ('id','name','created_at','target_at')
        #model = Todolist
        #sqla_session = db.session

todo_schema = TodolistSchema()
todos_schema = TodolistSchema(many=True)


##  To fetch our data from the database
##  using RESTful 'Resource'


class TodoResource(Resource):
    def get(self):
#we accept a GET request and make query to fetch all posts	
        ##ToDo_list = Todolist.query.all()
        ToDo_list = Todolist.query.order_by(Todolist.created_at).all()        
        #resp = make_response(render_template('/', **ToDo_list))
        #resp = jsonify(todos_schema.dump(ToDo_list)) #
        #index(ToDo_list)    #
        return jsonify(todos_schema.dump(ToDo_list))
		
#we accept a POST request, To add a new ToDo to the list      
    def post(self):
        if len(request.json['target_at']) == 10: # req from JSON    
            new_todo = Todolist(
                #name = request.form['name'],
                name = request.json['name'],
                target_at = request.json['target_at'],
            )
            db.session.add(new_todo)
            db.session.commit()
            ##for def save() 
            #new_todo.save()
            return jsonify(todo_schema.dump(new_todo))
        else:
            return jsonify({'result' : "Please enter proper FORMAT [YYYY-MM-DD] of Target Date for your ToDo."}) 

class TodolistResource(Resource):

##For Fetching particular ToDo
    def get(self, id):
        #ToDo_list = Todolist.query.order_by(Todolist.created_at).all()        
        one_todo = Todolist.query.filter(Todolist.id == id).one_or_none()
        
        #if id is not None:
        if id is not None:
            return jsonify(todo_schema.dump(one_todo))

        else:
            return jsonify({"result" : "!!Task not found for Id: {id}!!".format(id=id)}), 404
        
##For deleting        
    def delete(self, id):
        del_todo = Todolist.query.get_or_404(id)

        try:
            db.session.delete(del_todo)
            db.session.commit()
            #return redirect('/')
            return '', 204
        except:
            return jsonify({"result" : "There was a problem deleting new ToDo stuff."})

##For updating            
    def put(self, id):
        up_todo = Todolist.query.get_or_404(id)
        
        if 'name' in request.json:
            up_todo.name = request.json['name']

        if 'target_at' in request.json:
            if len(request.json['target_at']) == 10: # req from JSON        
                up_todo.target_at = request.json['target_at']
                try:
                    db.session.commit()
                    return todo_schema.dump(up_todo)
                    #title = "Update ToDo Data"
                    #return render_template('update.html', title=title, ToDo=up_todo)           
                except:
                    return jsonify({"result": "There was a problem updating ToDo data."})
            else:
                return jsonify({'result' : "Please add proper FORMAT [YYYY-MM-DD] of Target Date for your Updated ToDo."}) 


##For GET all / POST Method
api.add_resource(TodoResource, '/', '/api/todo/')

##For PUT Method (UPDATE) / GET / DELETE
api.add_resource(TodolistResource, '/api/todo/<int:id>' , '/api/update/<int:id>', '/api/delete/<int:id>')


##
def init_db():
    db.create_all()

if __name__ == '__main__':
    init_db()	# First time , it'll create all Tables
    app.run(debug=True)