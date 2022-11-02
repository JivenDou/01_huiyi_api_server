<?php
  // 时间: 2022/8/30
  // 功能: 返回历史数据请求的表格数据

  // 跨域解决
  header("Content-type:text/json;charset=UTF-8");
  header("Access-Control-Allow-Origin:*");
  include 'mysql.php';

  $input = file_get_contents("php://input");
  $input_json = json_decode($input);
  $start_time = $input_json->Start;
  $end_time = $input_json->End;

  if($start_time == $end_time){
    $sql = "SELECT id,times,ROUND(c1,2) c1,ROUND(c2,2) c2,ROUND(c3,2) c3,ROUND(c4,2) c4,ROUND(c5,2) c5,ROUND(c6,2) c6 FROM `table_shuizhi` WHERE date_format(times,'%Y-%m-%d')='$start_time';";
  }else{
    $sql = "SELECT id,times,ROUND(c1,2) c1,ROUND(c2,2) c2,ROUND(c3,2) c3,ROUND(c4,2) c4,ROUND(c5,2) c5,ROUND(c6,2) c6 FROM `table_shuizhi` WHERE times >= '$start_time 00:00:00' AND times <= '$end_time 23:59:59';";
  }
  $data=mysqli_query($conn,$sql);
  $result = [];
  while($row = $data->fetch_assoc()){
    array_push($result,$row);
  }
  
  if($start_time == $end_time){
    $sql = "SELECT id,times,ROUND(c7,2) c7 FROM `table_yelvsu` WHERE date_format(times,'%Y-%m-%d')='$start_time';";
  }else{
    $sql = "SELECT id,times,ROUND(c7,2) c7 FROM `table_yelvsu` WHERE times >= '$start_time 00:00:00' AND times <= '$end_time 23:59:59';";
  }
  $data=mysqli_query($conn,$sql);
  $get_yelvsu = [];
  while($row = $data->fetch_assoc()){
    array_push($get_yelvsu,$row);
  }

  if(count($result) == count($get_yelvsu)){
    for($i=0; $i<count($result); $i++){
      if($result[$i]['times'] == $get_yelvsu[$i]['times']){
        $result[$i]['c7'] = $get_yelvsu[$i]['c7'];
      }
    }
  }

  // 6.返回JSON类型的数据
  echo json_encode($result);
  // 7.关闭数据库
  $conn->close();