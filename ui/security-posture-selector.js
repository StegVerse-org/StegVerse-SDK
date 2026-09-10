(function(root){
  "use strict";
  var ORDER=["SECURE","HIGH","HIGHEST"];
  function rank(t){return ORDER.indexOf(String(t||""));}
  function render(el,model,onSelect){
    if(!el||!model||!model.automatic_posture||!model.effective_posture) throw new Error("security_posture_stack_model_required");
    var floor=model.automatic_posture.tier;
    var selected=(model.selected_posture&&model.selected_posture.tier)||floor;
    el.innerHTML="";
    el.classList.add("sv-security-posture");
    var summary=document.createElement("div");
    summary.className="sv-security-posture-summary";
    summary.innerHTML="<strong>Security posture</strong><span data-role='effective'>"+model.effective_posture.tier+"</span>";
    var detail=document.createElement("div");
    detail.className="sv-security-posture-detail";
    detail.innerHTML="<span>Automatic: <strong data-role='automatic'>"+floor+"</strong></span><span>Selected: <strong data-role='selected'>"+selected+"</strong></span>";
    var select=document.createElement("select");
    select.setAttribute("aria-label","Select security posture");
    ORDER.forEach(function(t){
      var opt=document.createElement("option"); opt.value=t; opt.textContent=t;
      opt.disabled=rank(t)<rank(floor); opt.selected=t===selected; select.appendChild(opt);
    });
    select.addEventListener("change",function(){
      if(rank(select.value)<rank(floor)){select.value=selected;return;}
      selected=select.value;
      detail.querySelector("[data-role='selected']").textContent=selected;
      summary.querySelector("[data-role='effective']").textContent=rank(selected)>rank(floor)?selected:floor;
      if(typeof onSelect==="function") onSelect(selected);
    });
    el.appendChild(summary); el.appendChild(detail); el.appendChild(select);
  }
  root.StegVerseSecurityPostureSelector={render:render,rank:rank,tiers:ORDER.slice()};
})(typeof globalThis!=="undefined"?globalThis:this);
