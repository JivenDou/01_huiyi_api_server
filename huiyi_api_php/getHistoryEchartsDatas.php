<?php
  // 时间: 2022/8/31
  // 功能: 返回历史数据请求的echarts数据

  // 跨域解决
  header("Content-type:text/json;charset=UTF-8");
  header("Access-Control-Allow-Origin:*");
  include 'mysql.php';

  $input = file_get_contents("php://input");
  $input_json = json_decode($input);

  $name = $input_json->Name;
  $start_time = $input_json->Start;
  $end_time = $input_json->End;

  $sqlDataName = array('温度'=>'c1','盐度'=>'c2','水深'=>'c3','浊度'=>'c4','溶解氧'=>'c6','PH值'=>'c5','叶绿素'=>'c7');

  if($name != '叶绿素'){
    if($start_time == $end_time){
      $sql = "SELECT times,ROUND($sqlDataName[$name],2) $sqlDataName[$name]  FROM `table_shuizhi` WHERE date_format(times,'%Y-%m-%d')='$start_time';";
    }else{
      $sql = "SELECT times,ROUND($sqlDataName[$name],2) $sqlDataName[$name] FROM `table_shuizhi` WHERE times >= '$start_time 00:00:00' AND times <= '$end_time 23:59:59';";
    }
  }else{
    if($start_time == $end_time){
      $sql = "SELECT times,ROUND($sqlDataName[$name],2) $sqlDataName[$name] FROM `table_yelvsu` WHERE date_format(times,'%Y-%m-%d')='$start_time';";
    }else{
      $sql = "SELECT times,ROUND($sqlDataName[$name],2) $sqlDataName[$name] FROM `table_yelvsu` WHERE times >= '$start_time 00:00:00' AND times <= '$end_time 23:59:59';";
    }
  }

  $data=mysqli_query($conn,$sql);
  $getData = [];

  while($row = $data->fetch_assoc()){
    array_push($getData,$row);
  }

  // 将时间数据提取成数组
  $resultTime = [];
  $resultData = [];
  for($i=0; $i<count($getData); $i++){
    array_push($resultTime,$getData[$i]['times']);
    array_push($resultData,$getData[$i][$sqlDataName[$name]]);
  }
  // 将提取的数据编成字典返回
  $result = array('time'=>$resultTime, 'value'=>$resultData);

  echo json_encode($result);
  // 7.关闭数据库
  $conn->close();