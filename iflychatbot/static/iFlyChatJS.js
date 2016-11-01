//<script type="text/javascript"> 


var userList = null;
var rawUserList = [
'Kris',
'Momotrader',
'Alphatrends',
'slystock',
'JasonW',
'FalloutDB',
'AimHigh',
'Optimus',
'Chartist',
'Vaiken',
'Nickthesure',
'Wildbuck',
'Stoxxx',
'JimmyV',
'Tedstocks',
'Cruiser',
'Candytreatme',
'bricklayer',
'BlueBrilliant',
'Fiverate',
'DimpleDoll',
'dodochip',
'fizzy',
'ninjastock',
'Tigerblood',
'born2trade',
'castbound',
'GreekGod',
'Battledoom',
'Castbound',
'coolguy',
'e4envy',
'MeatDuck',
'Jaycee',
'Max',
'wookie',
'WhackAttack12',
'Buckshot',
'bullfrog66',
'CyberKing',
'oblonggod',
'Kain',
'StockFreak',
'benzo33',
'TheRock',
'majestic',
'lightaswisha',
'Sgt.Traveler',
'AirFusion',
'aranamor',
'bosky2102',
'DaBomb',
'Zkyo',
'Techdopihn',
'OpelSpeedster',
'Napalm_bomb',
'grox19',
'geezyweezy',
'killerplant',
'Luvitus'
];

var lastCount = 0;
var realUsers = null;
var finalUsers = null;
window.iflychatAsyncInit = function() {
  
  // All iFlyChat related code should be defined here
  
  /** iFlyChat Init function **/

  iflychat.init({
  
    userlist : {
      visible: true
    }

  });

  /** iFlyChat ready event **/
  iflychat.on('ready', function() {
    console.log('iFlyChat Started');

    // Write your custom iFlyChat related code here

  }); 
iflychat.on('user-list-update', function(data) {
	console.log(data);
	lastCount = data.users.length;
  realUsers = data.users;

  reFillUserlist();

});

};

var avatarUrl = 'http://www.stocktips.chat/wp-content/uploads/2016/06/';

function prepareUserList() {
  var ret = new Array();
  for(var i=0;i<rawUserList.length;i++) {
    ret.push({ 'avatarUrl': avatarUrl + (i%10) + '.png', 'id': '-1', 'name': rawUserList[i], 'role': 'Bot', 'status': '1' });
  }
  for(var i=0;i<realUsers.length;i++) {
    ret.push({ 'avatarUrl': realUsers[i].avatarUrl, 'id': realUsers[i].id, 'name': realUsers[i].name, 'role': realUsers[i].role, 'status': realUsers[i].status });
  } 
  ret = ret.sort(function(a,b) {
    return a.name.toLowerCase().localeCompare(b.name.toLowerCase());
  }); 
  finalUsers = ret;
}

function reFillUserlist(num) {

  prepareUserList();

  jQuery(uls).innerHTML = '';
  console.log('Refilling userlist');
  var uls = jQuery('.subpanel > .item-list > ul')[0];
  uls.innerHTML = '';
  jQuery(uls).innerHTML = '';

for(var i=0;i<finalUsers.length;i++) {
    jQuery(uls).append('<li class="iflychat-olist-item iflychat-ol-ul-user-img iflychat-userlist-user-item role-0 role-s2member_level1"><span class="iflychat-olist-statuso"><span class="iflychat-olist-statusi-'+finalUsers[i].status+'"></span></span><img class="iflychat_ul_userimg" src="'+finalUsers[i].avatarUrl+'"><a class="'+finalUsers[i].id+'" href="#" id="drupalchat_user_"'+finalUsers[i].id+'">'+finalUsers[i].name+'</a></li>');
  }  
  setTimeout(reFillUserlist, 5000);
  jQuery('.subpanel > .item-list > ul').css('max-height', '550px');
//  var numUsers = 20 + Math.floor((Math.random() * 40) + 1);
  jQuery('.online-count').text(finalUsers.length);
}
//</script>