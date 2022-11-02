<?php
  // 时间: 2022/8/30
  // 功能: 返回实时数据请求的echarts用到的数据

  // 跨域解决
  header("Access-Control-Allow-Origin:*");
  // header("Content-type:application/json;charset=UTF-8");
  include 'mysql.php';

  $input = file_get_contents("php://input");
  $input_json = json_decode($input);
  $dateType = $input_json->dateType;
  $dataName = $input_json->dataName;

  date_default_timezone_set('PRC');
  $nowTime = date("Y-m-d H:i:s");
  $oneDayBeforeTime = date("Y-m-d H:i:s",strtotime("-1 day"));
  $sevenDayBeforeTime = date("Y-m-d H:i:s",strtotime("-7 day"));
  $thirtyDayBeforeTime = date("Y-m-d H:i:s",strtotime("-30 day"));
  $sqlDataName = array('Tem'=>'c1', 'Sal'=>'c2', 'Deep'=>'c3', 'Tur'=>'c4', 'Do'=>'c6', 'Ph'=>'c5', 'Chl'=>'c7');

  if($dataName != 'Chl'){
    if($dateType == 'hour'){
      $sql = "SELECT times,ROUND($sqlDataName[$dataName],2) $sqlDataName[$dataName] FROM `table_shuizhi` WHERE times >= '$oneDayBeforeTime' and times <= '$nowTime'";
    }elseif ($dateType == 'week') {
      $sql = "SELECT times,ROUND($sqlDataName[$dataName],2) $sqlDataName[$dataName] FROM `table_shuizhi` WHERE times >= '$sevenDayBeforeTime' and times <= '$nowTime'";
    }elseif ($dateType == 'month') {
      $sql = "SELECT times,ROUND($sqlDataName[$dataName],2) $sqlDataName[$dataName] FROM `table_shuizhi` WHERE times >= '$thirtyDayBeforeTime' and times <= '$nowTime'";
    }else{
      echo json_encode("{'msg': 'dateType error'}");
      $conn->close();
      exit();
    }
  }else{
    if($dateType == 'hour'){
      $sql = "SELECT times,ROUND($sqlDataName[$dataName],2) $sqlDataName[$dataName] FROM `table_yelvsu` WHERE times >= '$oneDayBeforeTime' and times <= '$nowTime'";
    }elseif ($dateType == 'week') {
      $sql = "SELECT times,ROUND($sqlDataName[$dataName],2) $sqlDataName[$dataName] FROM `table_yelvsu` WHERE times >= '$sevenDayBeforeTime' and times <= '$nowTime'";
    }elseif ($dateType == 'month') {
      $sql = "SELECT times,ROUND($sqlDataName[$dataName],2) $sqlDataName[$dataName] FROM `table_yelvsu` WHERE times >= '$thirtyDayBeforeTime' and times <= '$nowTime'";
    }else{
      echo json_encode("{'msg': 'dateType error'}");
      $conn->close();
      exit();
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
    array_push($resultData,$getData[$i][$sqlDataName[$dataName]]);
  }
  // 将提取的数据编成字典返回
  $result = array('time'=>$resultTime, 'value'=>$resultData);

  echo json_encode($result);
  // 7.关闭数据库
  $conn->close();