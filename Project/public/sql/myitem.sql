SET NAMES utf8;
DROP DATABASE IF EXISTS myitem;
CREATE DATABASE myitem CHARSET=utf8;
USE myitem;
CREATE TABLE t_user(
  uid INT PRIMARY KEY AUTO_INCREMENT,
  uname VARCHAR(50) NOT NULL DEFAULT '',
  upwd VARCHAR(32) NOT NULL DEFAULT '',
  regtime DATETIME NOT NULL DEFAULT 0
);
CREATE TABLE t_shoppingCart(
 sid INT PRIMARY KEY AUTO_INCREMENT,
 uid INT NOT NULL DEFAULT 0,
 pid INT NOT NULL DEFAULT 0,
 scount INT NOT NULL DEFAULT 0
);
CREATE TABLE t_product(
  pid INT PRIMARY KEY AUTO_INCREMENT,
  pname VARCHAR(100) NOT NULL DEFAULT '',
  pic VARCHAR(50) NOT NULL DEFAULT '',
  price DOUBLE(10,2) NOT NULL DEFAULT 0,
  lastprice DOUBLE(10,2) NOT NULL DEFAULT 0
);
CREATE TABLE t_order(
  oid INT PRIMARY KEY AUTO_INCREMENT,
  rcvName VARCHAR(32) NOT NULL DEFAULT '',
  price DECIMAL(10,2) NOT NULL DEFAULT 0,
  payment TINYINT,  /*1-在线支付 2-货到付款 3-京东白条*/
  orderTime BIGINT,
  status TINYINT,   /*1-等待付款  2-备货中  3-运输中  4-已签收*/
  userId INT NOT NULL DEFAULT 0
);

CREATE TABLE t_order_detail(
  did INT PRIMARY KEY AUTO_INCREMENT,
  orderId INT,
  productId INT,
  count INT
);

INSERT INTO t_order VALUES
(913431801,'tom123',1500, 1, 1401234567890,1, 1);


INSERT INTO t_order_detail VALUES
(NULL, 913431801, 10, 1),
(NULL, 913431801, 15, 3);

INSERT INTO t_product VALUES
(null,'蔓越莓100X2袋','img1/11.png',45,55),
(null,'美国原瓶进口米其林餐厅红酒','img1/21.jpg',99,152),
(null,'草莓夹心棉花糖办公室零食','img1/25.jpg',21,52),
(null,'风味苏打饼干','img1/35.png',20,25),
(null,'木椒盐味坚果','img1/36.jpg',10,11),
(null,'和田大红枣','img1/1.jpg',68,85),
(null,'抹茶蔓越莓饼干','img1/10.png',89,98),
(null,'新鲜肉松饼','img1/2.jpg',29,35),
(null,'潮汕猪肉脯','img1/3.jpg',25,32),
(null,'美味牛肉干','img1/7.jpg',50,56),
(null,'蔓越莓曲奇100X2袋','img1/15.png',44,55),
(null,'大连海鲜特产零食手撕碳烤鱿鱼丝','img1/16.png',20,22),
(null,'海南特产芒果干','img1/4.jpg',49,52),
(null,'苹果醋果醋醋饮料','img1/27.png',45,55),
(null,'米多奇馍香','img1/33.jpg',15,21),
(null,'韩国进口方便面三火养鸡','img1/22.jpg',42,50),
(null,'黑米蒸蛋糕小面包口袋面包','img1/26.png',79,89),
(null,'活力宝乳酸菌饮品','img1/28.png',18,21),
(null,'大连海鲜特产零食手撕碳烤鱿鱼','img1/12.png',25,35),
(null,'美味坚果','img1/8.jpg',15,22),
(null,'猪肉脯小包装猪肉铺蜜汁','img1/6.jpg',24,55),
(null,'盐焗腰果仁干货坚果零食','img1/5.jpg',45,55),
(null,'抹茶蔓越莓曲奇零食','img1/17.png',55,66),
(null,'绿色纯天然健康枣','img1/31.jpg',45,58),
(null,'巴旦木椒盐味','img1/32.jpg',32,48),
(null,'芒果夹心蛋糕','img1/42.png',25,38),
(null,'美味核桃','img1/41.png',25,38);
