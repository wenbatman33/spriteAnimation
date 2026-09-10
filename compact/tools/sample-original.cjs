// Sample the actual bundled Spine runtime so every export shares one timeline.
const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('assert');
const root=path.resolve(__dirname,'..'),stage='/Users/batman_work/codex-archives/five-original-production';
const ctx={console,Float32Array,Uint16Array,Int16Array,Uint32Array,Int32Array,Uint8Array,Math,window:{},navigator:{userAgent:''}};
vm.createContext(ctx);vm.runInContext(fs.readFileSync(path.join(root,'vendor/spine-player.js'),'utf8'),ctx);const s=ctx.spine;
const loader={newRegionAttachment:(_,name)=>{const a=new s.RegionAttachment(name);a.region={u:0,v:0,u2:1,v2:1,width:256,height:256,originalWidth:256,originalHeight:256,offsetX:0,offsetY:0,rotate:false};return a;}};
for(const id of process.argv.slice(2).length?process.argv.slice(2):['crown','thunder','app','line','duel']){
 const raw=JSON.parse(fs.readFileSync(path.join(stage,id,'spine-original/banner.json'))),sk=new s.Skeleton(new s.SkeletonJson(loader).readSkeletonData(raw)),state=new s.AnimationState(new s.AnimationStateData(sk.data));state.setAnimation(0,'idle',true);const frames=[];
 for(let i=0;i<120;i++){
  state.update(i?1/30:0.00001);state.apply(sk);sk.updateWorldTransform();
  frames.push(sk.drawOrder.filter(slot=>slot.attachment).map(slot=>{const a=slot.attachment,b=slot.bone;const matrix=[b.a,b.b,b.c,b.d,b.worldX,b.worldY];assert(matrix.every(Number.isFinite));return {name:a.name,slot:slot.data.name,matrix,width:a.width,height:a.height,alpha:slot.color.a*a.color.a,add:slot.data.blendMode===1};}));
 }
 assert(frames[0].length>=11);assert(new Set(frames.map(f=>f.map(x=>x.name).join('|'))).size>=(id==='vampire'?20:110));
 fs.writeFileSync(path.join(stage,id,'poses.json'),JSON.stringify(frames));console.log(id,'120 runtime poses',raw.bones.length,'bones');
}
