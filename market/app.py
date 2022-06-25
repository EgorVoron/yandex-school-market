from flask import Flask

import market.views as views
from market.db.schema import Base, ShopUnit, PriceUpdateLog
from market.db.sql_session import engine

#ShopUnit.__table__.drop(engine)  # upd
#PriceUpdateLog.__table__.drop(engine)  # upd

Base.metadata.create_all(engine)
app = Flask(__name__)

app.add_url_rule("/imports", methods=["POST"], view_func=views.imports)
app.add_url_rule("/delete/<id>", methods=["DELETE"], view_func=views.delete)
app.add_url_rule("/nodes/<id>", methods=["GET"], view_func=views.nodes)
app.add_url_rule("/sales", methods=["GET"], view_func=views.sales)

if __name__ == "__main__":
    app.run(debug=False, port=80)
