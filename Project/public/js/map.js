/**
 * Created by zhouli on 2017/5/28.
 */
////////map///////////////////////////

var map = new BMap.Map("cont");
var point = new BMap.Point(113.812519,22.733774);
map.centerAndZoom(point, 12);
map.enableScrollWheelZoom(true);

map.addControl(new BMap.NavigationControl());
map.addControl(new BMap.ScaleControl());
map.addControl(new BMap.OverviewMapControl());
map.addControl(new BMap.MapTypeControl());

var mk = new BMap.Marker(point);
map.addOverlay(mk);
mk.setAnimation(BMAP_ANIMATION_BOUNCE);