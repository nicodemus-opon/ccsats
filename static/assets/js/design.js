$('.subx').click(function () {
    var respo =$('.xcd').find('option:selected').text();
    console.log(respo)
    console.log("weeeee")
  $.ajax({
          type: 'POST',
          url: "{{ url_for('dashboard') }}",
          contentType: 'application/json;charset=UTF-8',
          //data : {'data':valuex},
          data: JSON.stringify(respo),
          //contentType: 'application/json',
          success: function (data) {
              // do something with the received data
              window.location.href = "/dashboard/table";
          }
      });
      window.location("/dashboard/table")
});