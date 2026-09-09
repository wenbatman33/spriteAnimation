// 直接增加資料與 assets 圖檔即可擴充內建動畫，不需 build。
export const animations = [
 {id:'gd-groove',name:'迷你 G-Dragon',subtitle:'G-DRAGON / CHIBI GROOVE',src:'./assets/gd-groove.png',columns:4,rows:2,count:8,fps:6,width:1536,height:1024,phases:['律動','下沉','抬手','交叉步','擺臂','換重心','開展','回拍']},
 {id:'hadouken',name:'波動拳',subtitle:'HADOUKEN / ARCADE FIGHTER',src:'./assets/fighter-projectile.png',columns:4,rows:2,count:8,fps:8,width:1536,height:1024,phases:['預備','蓄力','聚氣','推掌','發射','延伸','收招','復位'],clips:[
 ...[0,1,2,3].map(i=>({x:i*384,y:0,width:480,height:512,mask:'polygon(0 0,80% 0,80% 100%,0 100%)'})),
 {x:0,y:493,width:480,height:512,mask:'polygon(0 0,80% 0,80% 24%,89% 24%,89% 61%,80% 61%,80% 100%,0 100%)'},
 {x:384,y:493,width:480,height:512,mask:'polygon(10% 0,80% 0,80% 22%,100% 22%,100% 62%,80% 62%,80% 100%,0 100%,0 62%,10% 62%)'},
 {x:768,y:493,width:480,height:512,mask:'polygon(22% 0,80% 0,80% 100%,0 100%,0 62%,22% 62%)'},
 {x:1152,y:493,width:480,height:512,mask:'polygon(0 0,80% 0,80% 100%,0 100%)'}]}
];
