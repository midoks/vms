CREATE TABLE IF NOT EXISTS `video` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `name` TEXT,
  `filename` TEXT, 
  `size` INTEGER,
  `status` INTEGER,
  `node_num` INTEGER,
  `uptime` TEXT,
  `addtime` TEXT
);

CREATE TABLE IF NOT EXISTS `video_node` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `pid` INTEGER,
  `node_id` TEXT,
  `addtime` TEXT
);


CREATE TABLE IF NOT EXISTS `kv` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `name` TEXT,
  `value` TEXT,
  `addtime` TEXT
);

INSERT INTO `kv` (`id`, `name`, `value`, `addtime`) VALUES
(1, 'nginx_domain', '','2016-12-10 15:12:56');
INSERT INTO `kv` (`id`, `name`, `value`, `addtime`) VALUES
(2, 'nginx_listen', '0','2016-12-10 15:12:56');
INSERT INTO `kv` (`id`, `name`, `value`, `addtime`) VALUES
(3, 'nginx_path', '','2016-12-10 15:12:56');

