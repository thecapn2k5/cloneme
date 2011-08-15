// admins get these functions to modify the navigation
function ClonePrompt(text, id, cm){
   $("#clonemeprompt").clone().dialog({
      open: function(e, ui){
         $(this).attr('id', 'cloneprompt');
         $('#cloneprompt #clonetext').html(text + '<br>');
         $('#cloneprompt #saveid').val(id);
         $('#cloneprompt #savecm').val(cm);
         $('#cloneprompt #cloneinput').focus();
         $('#cloneprompt').removeClass('hideme');
      },
      close: function(e, ui){
         $(this).remove();
      }
   });
}

function SubmitPrompt(){
   var value = $('#cloneprompt #cloneinput').val();
   if (value){
      // vars
      var saveid = $('#cloneprompt #saveid').val();
      var id = saveid.replace(/\D/g, '')
      var savecm = $('#cloneprompt #savecm').val();

      if (savecm=='AddSideNav'){
         // adding a side nav
         $.getJSON('ajax.py', {'mode':"Home", 'cm':savecm, 'parent':Varparent(), 'name':value}, function(data){
            alert('Your page has been saved.  You need to refresh to see the page.');
         });
      } else {
         // adding or editing anything other than adding side nav
         $.getJSON('ajax.py', {'mode':"Home", 'cm':savecm, 'id':id, 'name':value}, function(data){
            if (id){
               // edit
               $('#' + saveid + ' a').html(value);
            } else {
               // they have added a new page
               alert('Your category has been saved.  You need to refresh to see the category.');
            }
         });
      }
   }
   $('#cloneprompt').remove()
}

function CloneConfirm(text, id, cm){
   $("#clonemeconfirm").clone().dialog({
      open: function(e, ui){
         $(this).attr('id', 'cloneconfirm');
         $('#cloneconfirm #clonetext').html(text + '<br>');
         $('#cloneconfirm #saveid').val(id);
         $('#cloneconfirm #savecm').val(cm);
         $('#cloneconfirm #ok').focus();
         $('#cloneconfirm').removeClass('hideme');
      },
      close: function(e, ui){
         $(this).remove();
      }
   });
}

function SubmitConfirm(){
   // vars
   var saveid = $('#cloneconfirm #saveid').val(); //navul2
   var id = saveid.replace(/\D/g, ''); //2
   var savecm = $('#cloneconfirm #savecm').val(); //DeleteTopNav

   $('#' + saveid).remove();

   $.getJSON('ajax.py', {'mode':"Home", 'cm':savecm, 'id':id}, function(data){
      if (savecm=='DeleteTopNav') {
         // if you're not on a static page, this will error
         if (Ifparent() && id == Varparent()){
            $('#cloneconfirm').remove()
            alert("You've deleted the category you're on.  You're being sent to the home page.");
            navigate('?')
            return
         }
      } else {
         // if you're not on a static page, this will error
         if (Ifstaticid() && id == Varstaticid()){
            $('#cloneconfirm').remove()
            alert("You've deleted the category you're on.  You're being sent to the home page.");
            navigate('?')
            return
         }
      }
   });
   $('#cloneconfirm').remove()
}
