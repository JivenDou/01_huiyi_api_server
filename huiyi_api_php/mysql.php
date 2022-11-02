<?php
require_once('config.php');
$conn = new mysqli($db_info['db_host'], $db_info['db_user'], $db_info['db_pwd'], $db_info['db_name']);
if ($conn->connect_error) {
    die("连接失败: " . $conn->connect_error);
}
mysqli_query($conn, "SET NAMES UTF8");
mysqli_set_charset($conn, 'utf8');