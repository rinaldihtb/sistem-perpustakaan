-- MySQL dump 10.13  Distrib 8.0.43, for macos15 (arm64)
--
-- Host: 127.0.0.1    Database: perpustakaan
-- ------------------------------------------------------
-- Server version	8.4.9

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `buku`
--

DROP TABLE IF EXISTS `buku`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `buku` (
  `id` int NOT NULL AUTO_INCREMENT,
  `judul` varchar(255) NOT NULL,
  `penulis` varchar(100) NOT NULL,
  `kategori` varchar(100) NOT NULL,
  `stok` int NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `buku`
--

LOCK TABLES `buku` WRITE;
/*!40000 ALTER TABLE `buku` DISABLE KEYS */;
INSERT INTO `buku` VALUES (1,'Laskar Pelangi','Andrea Hirata','Fiksi',9),(2,'Bumi Manusia','Pramoedya Ananta Toer','Fiksi',5),(3,'Sapiens','Yuval Noah Harari','Non-Fiksi',4),(4,'Atomic Habits','James Clear','Pengembangan Diri',7),(5,'Filosofi Teras','Henry Manampiring','Pengembangan Diri',8),(6,'Kamus Besar Bahasa Indonesia','Tim Balai Pustaka','Referensi',1),(7,'Ensiklopedia Sains Modern','Robert Winston','Referensi',2),(8,'Clean Code','Robert C. Martin','Teknologi',4),(9,'Python Crash Course','Eric Matthes','Teknologi',6),(10,'The Psychology of Money','Morgan Housel','Keuangan',6),(11,'Negeri 5 Menara','Ahmad Fuadi','Fiksi',7),(12,'Deep Work','Cal Newport','Produktivitas',4),(13,'Walaule','Penulis Walaule','Percakapan',0),(14,'Memasak','Chef Arnold','Memasak',5);
/*!40000 ALTER TABLE `buku` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `mahasiswa`
--

DROP TABLE IF EXISTS `mahasiswa`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `mahasiswa` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nim` varchar(20) NOT NULL,
  `nama` varchar(100) NOT NULL,
  `jurusan` varchar(100) NOT NULL,
  `tahun_masuk` int NOT NULL,
  `status_aktif` varchar(20) NOT NULL DEFAULT 'aktif',
  PRIMARY KEY (`id`),
  UNIQUE KEY `nim` (`nim`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `mahasiswa`
--

LOCK TABLES `mahasiswa` WRITE;
/*!40000 ALTER TABLE `mahasiswa` DISABLE KEYS */;
INSERT INTO `mahasiswa` VALUES (1,'10122101','Rian Hidayat','Teknik Informatika',2025,'aktif'),(2,'10122102','Dina Lestari','Sistem Informasi',2024,'aktif'),(3,'10122103','Eko Prasetyo','Teknik Elektro',2025,'aktif'),(4,'10122104','Fanya Amelia','Manajemen',2023,'aktif'),(5,'10122105','Gilang Perkasa','Akuntansi',2024,'aktif'),(6,'10122106','Hana Putri','Teknik Industri',2022,'aktif'),(7,'10122107','Ivan Saputra','Desain Komunikasi Visual',2023,'nonaktif'),(8,'10122108','Maya Safitri','Ilmu Komunikasi',2025,'aktif'),(9,'141110451','Rinaldi H','Teknik Informatika',2015,'aktif');
/*!40000 ALTER TABLE `mahasiswa` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `peminjaman`
--

DROP TABLE IF EXISTS `peminjaman`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `peminjaman` (
  `id` int NOT NULL AUTO_INCREMENT,
  `mahasiswa_id` int NOT NULL,
  `durasi` int NOT NULL,
  `status` varchar(20) NOT NULL DEFAULT 'draft',
  `dikembalikan` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `mahasiswa_id` (`mahasiswa_id`),
  CONSTRAINT `peminjaman_ibfk_1` FOREIGN KEY (`mahasiswa_id`) REFERENCES `mahasiswa` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=30 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `peminjaman`
--

LOCK TABLES `peminjaman` WRITE;
/*!40000 ALTER TABLE `peminjaman` DISABLE KEYS */;
INSERT INTO `peminjaman` VALUES (1,1,7,'disetujui',0),(2,2,5,'disetujui',1),(3,3,3,'ditolak',NULL),(4,4,7,'ditolak',NULL),(5,1,5,'disetujui',1),(6,5,10,'ditolak',NULL),(7,6,4,'disetujui',0),(8,4,10,'disetujui',1),(9,4,12,'disetujui',1),(10,4,12,'disetujui',0),(11,6,11,'ditolak',NULL),(12,1,12,'disetujui',0),(13,6,11,'ditolak',NULL),(14,6,14,'disetujui',1),(15,3,9,'disetujui',0),(16,5,8,'disetujui',0),(17,8,3,'ditolak',NULL),(18,3,13,'disetujui',1),(19,8,7,'ditolak',NULL),(20,1,12,'disetujui',0),(21,6,3,'ditolak',NULL),(22,6,6,'disetujui',0),(23,3,12,'disetujui',0),(24,1,5,'ditolak',NULL),(25,3,13,'disetujui',0),(26,8,12,'ditolak',NULL),(27,4,6,'ditolak',NULL),(28,8,30,'ditolak',NULL),(29,8,6,'disetujui',0);
/*!40000 ALTER TABLE `peminjaman` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `peminjaman_detail`
--

DROP TABLE IF EXISTS `peminjaman_detail`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `peminjaman_detail` (
  `id` int NOT NULL AUTO_INCREMENT,
  `peminjaman_id` int NOT NULL,
  `buku_id` int NOT NULL,
  `jumlah` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `peminjaman_id` (`peminjaman_id`),
  KEY `buku_id` (`buku_id`),
  CONSTRAINT `peminjaman_detail_ibfk_1` FOREIGN KEY (`peminjaman_id`) REFERENCES `peminjaman` (`id`),
  CONSTRAINT `peminjaman_detail_ibfk_2` FOREIGN KEY (`buku_id`) REFERENCES `buku` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=34 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `peminjaman_detail`
--

LOCK TABLES `peminjaman_detail` WRITE;
/*!40000 ALTER TABLE `peminjaman_detail` DISABLE KEYS */;
INSERT INTO `peminjaman_detail` VALUES (1,1,1,1),(2,1,4,1),(3,2,2,1),(4,2,5,1),(5,3,3,1),(6,4,8,1),(7,5,6,1),(8,6,9,2),(9,7,10,1),(10,7,12,1),(11,8,5,3),(12,9,10,2),(13,10,6,2),(14,11,6,1),(15,12,12,3),(16,13,10,1),(17,14,1,3),(18,15,4,3),(19,16,7,3),(20,17,10,3),(21,18,5,2),(22,19,4,3),(23,20,10,2),(24,21,10,2),(25,22,3,1),(26,23,12,3),(27,24,1,3),(28,25,12,2),(29,26,11,1),(30,27,12,1),(31,28,12,3),(32,29,6,2),(33,29,13,1);
/*!40000 ALTER TABLE `peminjaman_detail` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-07-04  4:02:57
