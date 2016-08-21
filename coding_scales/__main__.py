import sys
try:
    from .coding_scales import (app,
                                db,
                                User,
                                Exercise,
                                Result)
except SystemError:
    from coding_scales import (app,
                                db,
                                User,
                                Exercise,
                                Result)


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
    exercise_2 = Exercise(author_id=admin.id,
                          text='print("hello, world!")\n',
                          language="python",
                          name="hello-world.py")
    exercise_1 = Exercise(author_id=admin.id,
                          text='a, b = b, a\n',
                          language="python",
                          name="variable-swap.py")
    db.session.add_all([exercise_1, exercise_2])
    db.session.commit()
    db.session.add(Result(user_id=admin.id,
                          exercise_id=exercise_1.id,
                          time=2,
                          keypresses=14))
    db.session.commit()
if "run" in sys.argv:
    app.run(debug=True)
