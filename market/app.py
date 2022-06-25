from flask import Flask

import market.views as views
from market.db.schema import Base
from market.db.sql_session import engine

Base.metadata.create_all(engine)
app = Flask(__name__)

# I've decided to use add_url_rule() instead of decorators in order to
# easily split creating app and declarations of routes from routes' implementations
app.add_url_rule("/imports", methods=["POST"], view_func=views.imports)
app.add_url_rule("/delete/<id>", methods=["DELETE"], view_func=views.delete)
app.add_url_rule("/nodes/<id>", methods=["GET"], view_func=views.nodes)
app.add_url_rule("/sales", methods=["GET"], view_func=views.sales)

if __name__ == "__main__":
    app.run(debug=False, port=80)
