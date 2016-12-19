import os
import sys
import json
try:
    from .coding_scales import (app,db,User,Exercise,Result)
except:
    from coding_scales import (app,db,User,Exercise,Result)


if "init" in sys.argv:
    db.drop_all()
    db.session.commit()
    db.create_all()
    admin = User(username="admin",
                 password="admin",
                 email="1@test.com")
    user_1 = User(username="user-1",
                 password="pass",
                 email="2@test.com")
    user_2 = User(username="user-2",
                 password="pass",
                 email="3@test.com")
    admin.role = "admin"
    db.session.add(admin)
    db.session.add(user_1)
    db.session.add(user_2)
    db.session.commit()
    filename = os.path.join(os.path.dirname(__file__), "sample-idioms.json")
    with open(filename, "r") as fp:
        exercises = json.load(fp)
    exercises = [Exercise(**kwargs) for kwargs in exercises]
    db.session.add_all(exercises)
    db.session.commit()
if "run" in sys.argv:
    app.run(debug=True)
