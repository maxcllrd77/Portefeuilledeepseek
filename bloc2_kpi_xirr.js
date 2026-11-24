var _xr=window._PF?computeRealReturn(window._PF,V):null;
var _kl=_xr!==null?"Rendement réel (XIRR)":"Gain / perte";
var _kv=_xr!==null?"<b class='"+(_xr>=0?"up":"dn")+"'>"+f(_xr,1)+" %</b>":"<b class='"+(G>=0?"up":"dn")+"'>"+f(G,0)+" € ("+f(G/CK*100,1)+" %)</b>";
document.getElementById("kp").innerHTML="<div><span class='s'>Valeur</span><b>"+V.toFixed(0)+" €</b></div><div><span class='s'>Investi</span><b>"+CK.toFixed(0)+" €</b></div><div><span class='s'>"+_kl+"</span>"+_kv+"</div>";
