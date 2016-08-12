import sys
from .coding_scales import (app,
                            configure_app,
                            db,
                            User,
                            Exercise,
                            Result)

if "init" in sys.argv:
    db.drop_all()
    db.session.commit()
    db.create_all()
    user_1 = User(username="test-user-1",
                  password="test-pass",
                  email="1@test.com")
    user_2 = User(username="test-user-2",
                  password="test-pass",
                  email="2@test.com")
    db.session.add(user_1)
    db.session.add(user_2)
    db.session.commit()
    exercise_1 = Exercise(author_id=user_1.id,
                          text='print("hello, world!")\n',
                          language="python",
                          name="user-1-hello-world")
    exercise_2 = Exercise(author_id=user_2.id,
                          text='print("hello, world!")\n',
                          language="Python",
                          name="user-2-hello-world")
    db.session.add(exercise_1)
    db.session.add(exercise_2)
    db.session.commit()
    db.session.add_all([Result(user_id=user_1.id,
                               exercise_id=exercise_1.id,
                               time=2),
                        Result(user_id=user_2.id,
                               exercise_id=exercise_2.id,
                               time=2)])
    db.session.commit()
if "run" in sys.argv:
    configure_app()
    app.run()
