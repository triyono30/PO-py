-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Feb 02, 2026 at 04:00 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `po_db`
--

-- --------------------------------------------------------

--
-- Table structure for table `barang`
--

CREATE TABLE `barang` (
  `id_barang` varchar(20) NOT NULL,
  `id_supplier` varchar(20) DEFAULT NULL,
  `nama_barang` varchar(100) DEFAULT NULL,
  `harga` decimal(12,2) DEFAULT NULL,
  `stok` int(11) DEFAULT NULL,
  `spek` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `barang`
--

INSERT INTO `barang` (`id_barang`, `id_supplier`, `nama_barang`, `harga`, `stok`, `spek`) VALUES
('BRG01', 'SUP002', 'Kertas F4', 55000.00, 103, NULL),
('BRG02', 'SUP01', 'Pulpen', 3000.00, 514, NULL),
('BRG03', 'SUP01', 'Tinta Printer', 120000.00, 62, NULL),
('BRG04', 'SUP01', 'Kertas A4', 55000.00, 108, NULL);

-- --------------------------------------------------------

--
-- Table structure for table `po`
--

CREATE TABLE `po` (
  `id_po` varchar(30) NOT NULL,
  `tanggal_order` date NOT NULL,
  `nama_pemesan` varchar(100) NOT NULL,
  `tanggal_kirim` date DEFAULT NULL,
  `id_supplier` varchar(20) DEFAULT NULL,
  `alamat_kirim` text DEFAULT NULL,
  `status_order` enum('DRAFT','ORDER','DIKIRIM','SELESAI','BATAL') DEFAULT 'ORDER',
  `total` decimal(12,2) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `po`
--

INSERT INTO `po` (`id_po`, `tanggal_order`, `nama_pemesan`, `tanggal_kirim`, `id_supplier`, `alamat_kirim`, `status_order`, `total`) VALUES
('PO-202601-SUP01-0001', '2026-01-31', '', '2026-02-05', 'SUP01', 'Jl. Industri No 10, Bandung', 'ORDER', 110000.00),
('PO-202602-SUP002-0001', '2026-02-01', 'try', '2026-02-10', 'SUP002', 'YY', 'ORDER', 110000.00),
('PO-202602-SUP002-0002', '2026-02-01', 'try', '2026-02-19', 'SUP002', 'try', 'ORDER', 55000.00),
('PO-202602-SUP01-0001', '2026-01-31', 'try', '2026-03-06', 'SUP01', 'try', 'ORDER', 30000.00),
('PO-202602-SUP01-0002', '2026-01-31', 'try', '2026-02-25', 'SUP01', 'tryy', 'ORDER', 275000.00),
('PO-202602-SUP01-0003', '0000-00-00', 'try', '2026-02-12', 'SUP01', 'TRY', 'ORDER', 411000.00),
('PO-202602-SUP01-0004', '2026-02-01', 'try', '2026-02-11', 'SUP01', 'try', 'ORDER', 6000.00),
('PO-202602-SUP01-0005', '2026-02-01', 'try', '2026-02-18', 'SUP01', 'yyy', 'ORDER', 1200000.00);

-- --------------------------------------------------------

--
-- Table structure for table `po_detail`
--

CREATE TABLE `po_detail` (
  `id_detail` int(11) NOT NULL,
  `id_po` varchar(30) DEFAULT NULL,
  `id_barang` varchar(20) DEFAULT NULL,
  `qty` int(11) DEFAULT NULL,
  `harga` decimal(12,2) DEFAULT NULL,
  `subtotal` decimal(12,2) DEFAULT NULL,
  `ket` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `po_detail`
--

INSERT INTO `po_detail` (`id_detail`, `id_po`, `id_barang`, `qty`, `harga`, `subtotal`, `ket`) VALUES
(1, 'PO-202601-SUP01-0001', 'BRG01', 2, 55000.00, 110000.00, NULL),
(2, 'PO-202602-SUP01-0001', 'BRG02', 10, 3000.00, 30000.00, NULL),
(3, 'PO-202602-SUP01-0002', 'BRG04', 5, 55000.00, 275000.00, NULL),
(4, 'PO-202602-SUP01-0003', 'BRG02', 2, 3000.00, 6000.00, NULL),
(5, 'PO-202602-SUP01-0003', 'BRG04', 3, 55000.00, 165000.00, NULL),
(6, 'PO-202602-SUP01-0003', 'BRG03', 2, 120000.00, 240000.00, NULL),
(7, 'PO-202602-SUP01-0004', 'BRG02', 2, 3000.00, 6000.00, NULL),
(8, 'PO-202602-SUP002-0001', 'BRG01', 2, 55000.00, 110000.00, NULL),
(9, 'PO-202602-SUP01-0005', 'BRG03', 10, 120000.00, 1200000.00, NULL),
(10, 'PO-202602-SUP002-0002', 'BRG01', 1, 55000.00, 55000.00, NULL);

-- --------------------------------------------------------

--
-- Table structure for table `supplier`
--

CREATE TABLE `supplier` (
  `id_supplier` varchar(20) NOT NULL,
  `nama_supplier` varchar(100) DEFAULT NULL,
  `alamat` text DEFAULT NULL,
  `telp` varchar(20) DEFAULT NULL,
  `status` tinyint(1) NOT NULL DEFAULT 1 COMMENT '1=Aktif, 0=Non Aktif'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `supplier`
--

INSERT INTO `supplier` (`id_supplier`, `nama_supplier`, `alamat`, `telp`, `status`) VALUES
('SUP002', 'CV. Nusantara Abadi', 'Jl. Sudirman No. 45, Bandung', '022-7654321', 1),
('SUP003', 'PT. Indo Jaya', 'Jl. Pahlawan No. 78, Surabaya', '031-9876543', 0),
('SUP004', 'CV. Sentosa Sejahtera', 'Jl. Gatot Subroto No. 12, Medan', '061-1122334', 0),
('SUP005', 'PT. Mega Prima', 'Jl. Diponegoro No. 5, Yogyakarta', '0274-556677', 0),
('SUP006', 'PT. Sumber Makmur', 'Jl. Merdeka No. 10, Jakarta', '021-1234567', 1),
('SUP01', 'PT Maju Jaya', 'Bandung', '08123456789', 1);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `barang`
--
ALTER TABLE `barang`
  ADD PRIMARY KEY (`id_barang`),
  ADD KEY `fk_barang_supplier` (`id_supplier`);

--
-- Indexes for table `po`
--
ALTER TABLE `po`
  ADD PRIMARY KEY (`id_po`),
  ADD KEY `id_supplier` (`id_supplier`);

--
-- Indexes for table `po_detail`
--
ALTER TABLE `po_detail`
  ADD PRIMARY KEY (`id_detail`),
  ADD KEY `id_barang` (`id_barang`),
  ADD KEY `id_po` (`id_po`) USING BTREE;

--
-- Indexes for table `supplier`
--
ALTER TABLE `supplier`
  ADD PRIMARY KEY (`id_supplier`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `po_detail`
--
ALTER TABLE `po_detail`
  MODIFY `id_detail` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `barang`
--
ALTER TABLE `barang`
  ADD CONSTRAINT `fk_barang_supplier` FOREIGN KEY (`id_supplier`) REFERENCES `supplier` (`id_supplier`) ON UPDATE CASCADE;

--
-- Constraints for table `po`
--
ALTER TABLE `po`
  ADD CONSTRAINT `po_ibfk_1` FOREIGN KEY (`id_supplier`) REFERENCES `supplier` (`id_supplier`);

--
-- Constraints for table `po_detail`
--
ALTER TABLE `po_detail`
  ADD CONSTRAINT `po_detail_ibfk_1` FOREIGN KEY (`id_po`) REFERENCES `po` (`id_po`),
  ADD CONSTRAINT `po_detail_ibfk_2` FOREIGN KEY (`id_barang`) REFERENCES `barang` (`id_barang`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
