const preset=document.querySelector('#preset'),role=document.querySelector('#role'),platform=document.querySelector('#platform'),command=document.querySelector('#command'),score=document.querySelector('#score'),bar=document.querySelector('#bar');
function render(){
 const p=preset.value,r=role.value,w=platform.value;
 let s=95;if(p==='developer')s-=3;if(r==='server')s-=2;if(p==='strict')s=99;if(p==='minimal')s=97;
 score.textContent=`${s} / 100`;bar.style.width=`${s}%`;
 const args=`--preset ${p} --role ${r}`;
 if(w==='windows') command.textContent=`gh repo clone JDsnyke/hermes-privacy-stack "$HOME\\.hermes-privacy-stack" -- --depth 1; & "$HOME\\.hermes-privacy-stack\\install.ps1" ${args}`;
 else command.textContent=`gh repo clone JDsnyke/hermes-privacy-stack "$HOME/.hermes-privacy-stack" -- --depth 1 && "$HOME/.hermes-privacy-stack/install.sh" ${args}`;
}
[preset,role,platform].forEach(x=>x.addEventListener('change',render));
document.querySelector('#copy').addEventListener('click',async e=>{await navigator.clipboard.writeText(command.textContent);e.target.textContent='Copied ✓';setTimeout(()=>e.target.textContent='Copy command',1200)});render();
