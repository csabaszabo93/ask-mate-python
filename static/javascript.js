$('#exampleModal').on('shown.bs.modal', function () {
  alert("{{show_modal}}")
});
$(document).ready(function(){
    $("#exampleModal").modal('show');
    alert('maci')
});