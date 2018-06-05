-- 用户添加超级用户
ALTER TABLE `auth_group` CHANGE `name` `name` VARCHAR(80) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL;
ALTER TABLE `admin` ADD `is_superuser` TINYINT(1) NOT NULL DEFAULT '0' COMMENT '超级用户' AFTER `is_staff`;
ALTER TABLE `admin` ADD `first_name` VARCHAR(30) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL AFTER `is_superuser`;
ALTER TABLE `admin` ADD `last_name` VARCHAR(30) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL AFTER `first_name`;
ALTER TABLE `admin` ADD `email` VARCHAR(150) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL AFTER `last_name`;
ALTER TABLE `admin` ADD `date_joined` DATETIME NOT NULL DEFAULT '0000-00-00 00:00:00' AFTER `email`;


 CREATE TABLE `auth_user_user_permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
ALTER TABLE `auth_user_user_permissions` ADD INDEX(`user_id`);
ALTER TABLE `auth_user_user_permissions` ADD INDEX(`permission_id`);



auth_user_groups | CREATE TABLE `auth_user_groups` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
ALTER TABLE `auth_user_groups` ADD INDEX(`user_id`);
ALTER TABLE `auth_user_groups` ADD INDEX(`group_id`);



CREATE TABLE `perm_mypermission` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `parent_id` int(11) DEFAULT NULL COMMENT '父ID',
  `permission_id` int(11) DEFAULT NULL COMMENT '权限ID',
  `name` varchar(50) NOT NULL COMMENT '权限名称',
  `is_nav` tinyint(1) NOT NULL DEFAULT '1' COMMENT '是否为导航',
  `nav_name` varchar(50) NOT NULL COMMENT '导航名称',
  `url` varchar(150) DEFAULT NULL COMMENT '目录url',
  `is_default` tinyint(1) NOT NULL DEFAULT '0' COMMENT '是否为默认权限',
  `order_id` int(11) NOT NULL DEFAULT '1' COMMENT '导航顺序',
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `parent_id` (`parent_id`),
  KEY `permission_id` (`permission_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
ALTER TABLE `perm_mypermission` ADD INDEX(`url`);
