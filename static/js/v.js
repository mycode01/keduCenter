$(document).ready(function(){

    $('a.btn').bind('click', function(e){
        $('a.btn').attr('disabled', 'disabled');
        if($(this).attr('id') == 'btn-pid'){
            getID();
        } else {
            process();
        }
    })

});


var styles = [
    'background: linear-gradient(#D33106, #571402)'
    , 'border: 1px solid #3E0E02'
    , 'color: white'
    , 'display: block'
    , 'text-shadow: 0 1px 0 rgba(0, 0, 0, 0.3)'
    , 'box-shadow: 0 1px 0 rgba(255, 255, 255, 0.4) inset, 0 5px 3px -5px rgba(0, 0, 0, 0.5), 0 -13px 5px -10px rgba(255, 255, 255, 0.4) inset'
    , 'line-height: 40px'
    , 'text-align: center'
    , 'font-weight: bold'
].join(';');

console.log('%c there is nothing to see here ', styles);


var getID = function (){
    $.post('/getID', {"cstring":$('#cstring').val()},function(data){ console.log(data) }).done(function(data){
         $('#pid').val(data.pid)
         $('a.btn').attr('disabled', false);
         alert('pid 로드');
         }).fail(error);
    $('#cstring').attr('readonly',true);
    $('#pid').attr('readonly',true);
};

var process = function(){
    $.post('/process', {"cstring":$('#cstring').val(), "pid":$('#pid').val(), "order":$('#order').val()[0]}, function(data){
    console.log(data);}).done(function(data){
    $('a.btn').attr('disabled', false);
    alert('회차 완료!');
    if(data.order == '20'){
        alert('모든 회차가 완료되었습니다.');
    } else {
        $('#order').val(data.order*1+1)
    }
    }).fail(error);
}

function error(data){
        alert('에러발생, 중단 하시고 "저"에게 알려주세요.');
    }

function jsonp_callback(data)
{
    console.log(data);
}