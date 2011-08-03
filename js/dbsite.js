// admins get these functions to modify the top nav
function DeleteTopNav(id){
   if(confirm('Are you sure you want to permanently delete this category and all pages associated with it?')){
      $.getJSON('ajax.py', {'mode':"Home", 'cm':'DeleteTopNav', 'id':id}, function(data){
         if (Ifparent()){
            // if you're not on a static page, this will error
            if(data['id'] == Varparent()){
               alert("You've deleted the category you're on.  You're being sent to the home page.");
               navigate('?')
               return
            }
         }
         location.reload(true);
      });
   }
}

function EditTopNav(id, name){
   var newname = prompt("Please put in the new name for " + name + ".")
   if(newname){
      $.getJSON('ajax.py', {'mode':"Home", 'cm':'EditTopNav', 'id':id, 'name':newname}, function(data){
         location.reload(true);
      });
   }
}

function AddTopNav(){
   var name = prompt("Please put in the name for the new category.")
   if(name){
      $.getJSON('ajax.py', {'mode':"Home", 'cm':'AddTopNav', 'name':name}, function(data){
         location.reload(true);
      });
   }
}

// admins get these functions to modify the side nav
function DeleteSideNav(id){
   if(confirm('Are you sure you want to permanently delete this page?')){
      $.getJSON('ajax.py', {'mode':"Home", 'cm':'DeleteSideNav', 'id':id}, function(data){
         if (Ifstaticid()){
            // if you're not on a static page, this will error
            if(data['id'] == Varstaticid()){
               alert("You've deleted the page you're on.  You're being sent to the home page.");
               navigate('?')
               return
            }
         }
         location.reload(true);
      });
   }
}

function EditSideNav(id, name){
   var newname = prompt("Please put in the new name for " + name + ".")
   if(newname){
      $.getJSON('ajax.py', {'mode':"Home", 'cm':'EditSideNav', 'id':id, 'name':newname}, function(data){
         location.reload(true);
      });
   }
}

function AddSideNav(){
   var name = prompt("Please put in the name for the new page.")
   if(name){
      $.getJSON('ajax.py', {'mode':"Home", 'cm':'AddSideNav', 'parent':Varparent(), 'name':name}, function(data){
         location.reload(true);
      });
   }
}
