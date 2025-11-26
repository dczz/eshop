|业务领域 (Business Domain)|核心功能 (Key Functionalities)   |对应的单体模块 (Monolithic Module)|
|----------------------|-----------------------------|---------------------------|
|1. 商品目录 (Catalog)     |商品管理： - 查看所有商品列表。 - 按品牌、类型等进行筛选和分页。 - 查看单个商品的详细信息。 - 维护库存数量（Inventory Management, 隐含）。|CatalogService / ProductModel|
|2. 购物车 (Basket/Cart)  |购物车管理： - 将商品添加到购物车。 - 更新购物车中商品的数量。 - 从购物车中删除商品。 - 查看购物车的总金额。 - 将购物车与用户身份关联（持久化）。|BasketService / CartModel  |
|3. 订单处理 (Ordering)    |订单生命周期： - 从购物车创建新订单（结账）。 - 记录订单详情（商品、数量、价格）。 - 处理收货地址和支付信息（可能为模拟支付）。 - 查看用户的历史订单列表。 - 查看单个订单的详细信息和状态（如待支付、已发货、已完成）。|OrderService / OrderModel  |
|4. 身份与认证 (Identity & Auth)|用户管理与安全： - 用户注册和登录（Authentication）。 - 权限验证（Authorization，例如只有登录用户才能结账）。 - 用户信息管理（如收货地址、联系方式）。|UserService / AuthService  |
|5. 营销与促销 (Marketing/Campaigns)|（可选/扩展功能）： - 显示促销活动或优惠券信息（在原 eShop 项目中，这通常是独立服务）。|MarketingService           |


```text
/app
  /routers
    /catalog.py     # 包含所有商品目录的 API 路由
    /basket.py      # 包含购物车相关的 API 路由
    /ordering.py    # 包含订单创建和查询的 API 路由
    /auth.py        # 包含用户注册和登录的 API 路由
  /services
    /catalog_service.py
    /basket_service.py
    /order_service.py
  /schemas # Pydantic 模型
  /models # SQLAlchemy 模型
    /product.py     
    /cart_item.py
    /order.py
    /user.py
```