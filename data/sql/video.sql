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

