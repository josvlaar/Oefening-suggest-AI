-- --------------------------------------------------------
-- Host:                         127.0.0.1
-- Server version:               8.0.31 - MySQL Community Server - GPL
-- Server OS:                    Win64
-- HeidiSQL Version:             12.1.0.6537
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


-- Dumping database structure for sample1
DROP DATABASE IF EXISTS `sample1`;
CREATE DATABASE IF NOT EXISTS `sample1` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `sample1`;

-- Dumping structure for table sample1.answers
DROP TABLE IF EXISTS `answers`;
CREATE TABLE IF NOT EXISTS `answers` (
  `id` int NOT NULL AUTO_INCREMENT,
  `question_id` int NOT NULL,
  `shortanswer` char(1) NOT NULL,
  `answer` text NOT NULL,
  PRIMARY KEY (`id`),
  KEY `question_id` (`question_id`),
  CONSTRAINT `answers_ibfk_1` FOREIGN KEY (`question_id`) REFERENCES `questions` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Dumping data for table sample1.answers: ~14 rows (approximately)
REPLACE INTO `answers` (`id`, `question_id`, `shortanswer`, `answer`) VALUES
	(1, 1, 'A', 'Alfabet'),
	(2, 1, 'B', 'Bal'),
	(3, 2, 'A', 'Alfabet'),
	(4, 2, 'B', 'Bal'),
	(5, 2, 'C', 'Cool'),
	(6, 3, 'A', 'Alfabet'),
	(7, 3, 'B', 'Bal'),
	(8, 3, 'C', 'Cool'),
	(9, 3, 'D', 'Dweil'),
	(10, 4, 'A', 'Alfabet'),
	(11, 4, 'B', 'Bal'),
	(12, 4, 'C', 'Cool'),
	(13, 4, 'D', 'Dweil'),
	(14, 4, 'E', 'Elfje');

-- Dumping structure for table sample1.answersgiven
DROP TABLE IF EXISTS `answersgiven`;
CREATE TABLE IF NOT EXISTS `answersgiven` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `question_id` int NOT NULL,
  `answer_id` int NOT NULL,
  `timeelapsed` float NOT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `question_id` (`question_id`),
  KEY `answer_id` (`answer_id`),
  CONSTRAINT `answersgiven_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `answersgiven_ibfk_2` FOREIGN KEY (`question_id`) REFERENCES `questions` (`id`),
  CONSTRAINT `answersgiven_ibfk_3` FOREIGN KEY (`answer_id`) REFERENCES `answers` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Dumping data for table sample1.answersgiven: ~0 rows (approximately)

-- Dumping structure for table sample1.questions
DROP TABLE IF EXISTS `questions`;
CREATE TABLE IF NOT EXISTS `questions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `question` text NOT NULL,
  `correctanswer` char(1) NOT NULL,
  `avgtime` float DEFAULT NULL,
  `numofanswers` int DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Dumping data for table sample1.questions: ~4 rows (approximately)
REPLACE INTO `questions` (`id`, `question`, `correctanswer`, `avgtime`, `numofanswers`) VALUES
	(1, 'A?', 'A', NULL, NULL),
	(2, 'B?', 'B', NULL, NULL),
	(3, 'C?', 'C', NULL, NULL),
	(4, 'D?', 'D', NULL, NULL);

-- Dumping structure for table sample1.users
DROP TABLE IF EXISTS `users`;
CREATE TABLE IF NOT EXISTS `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `avgtime` float DEFAULT NULL,
  `numofquestions` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Dumping data for table sample1.users: ~4 rows (approximately)
REPLACE INTO `users` (`id`, `name`, `avgtime`, `numofquestions`) VALUES
	(1, 'Jos', NULL, NULL),
	(2, 'Jan', NULL, NULL),
	(3, 'Stefan', NULL, NULL),
	(4, 'Korian', NULL, NULL);

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
