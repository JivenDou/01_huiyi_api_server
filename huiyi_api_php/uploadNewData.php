<?php
  // 时间：2022-09-07
  // 功能：将传感器数据传到云端
  header("Content-type:text/json;charset=UTF-8");
  // header("Access-Control-Allow-Origin:*");
  include 'mysql.php';

  $input = file_get_contents("php://input");
  $input_json = json_decode($input);
  
  $id = $input_json->id;
  $times = $input_json->times;
  $c1 = $input_json->c1;
  $c2 = $input_json->c2;
  $c3 = $input_json->c3;
  $c4 = $input_json->c4;
  $c5 = $input_json->c5;
  $c6 = $input_json->c6;
  $c7 = $input_json->c7;

  $sql = "INSERT INTO `table_shuizhi`(id,times,c1,c2,c3,c4,c5,c6,c7) VALUES($id,'$times',$c1,$c2,$c3,$c4,$c5,$c6,$c7)";
  // 执行sql语句
  mysqli_query($conn,$sql);
  
  // var_dump("success");
  echo json_encode("{'msg':'success'}");
  // echo json_encode($input_json);

