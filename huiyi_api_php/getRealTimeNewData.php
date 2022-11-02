<?php
  // 时间：2022-08-29
  // 功能：获取最新一条数据

  // 跨域解决
  header("Content-type:text/json;charset=UTF-8");
  // header("Access-Control-Allow-Origin:*");
  include 'mysql.php';


  $sql = "SELECT ROUND( c1, 2 ) as c1,ROUND(c2, 2 ) as c2,ROUND(c3,2 ) as c3, ROUND( c4, 2 ) as c4,ROUND(c5, 2 ) as c5,ROUND(c6,2 ) as c6 FROM `table_shuizhi` ORDER BY times DESC LIMIT 1";
  // $result = $conn->query($sql)->fetch_all(MYSQLI_ASSOC);
  $data = mysqli_query($conn,$sql);
  $result = [];
  while($row = mysqli_fetch_array($data,MYSQLI_ASSOC)){
    $result[0] = $row;
  }

  $sql = "SELECT ROUND( c7, 2 ) as c7 FROM `table_yelvsu` ORDER BY times DESC LIMIT 1";
  $data = mysqli_query($conn,$sql);
  $get_yelvsu = mysqli_fetch_array($data,MYSQLI_ASSOC);
  $result[0]['c7'] = $get_yelvsu['c7'];
  
  // 6.返回JSON类型的数据
  echo json_encode($result);
  // 7.关闭数据库
  $conn->close();