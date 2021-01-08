CREATE TABLE IF NOT EXISTS `video` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `name` TEXT,
  `filename` TEXT, 
  `size` INTEGER,
  `status` INTEGER,
  `uptime` TEXT,
  `addtime` TEXT
);

INSERT INTO `video` (`id`, `name`, `filename`, `size`, `status`, `addtime`) VALUES
(1, '21232f297a57a5a743894a0e4a801fc3', '12', '12', 0, '2016-12-10 15:12:56','2016-12-10 15:12:56');