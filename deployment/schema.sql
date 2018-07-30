-- schema for MySQL
create table 'UploadedFiles' (
  `id` int(11) not null auto_increment,
  `filename` varchar(5000) not null,
  `filehash` varchar(128) not null,
  `filemd5` varchar(128) not null,
  `uploaded_time` datetime not null,
  `mimetype` varchar(256) not null,
  `size` int(11) unsigned not null,
  primary key (`id`) `,
  unique key ` filehash` (`filehash`)
) engine=InnoDB default charset=utf8mb4;