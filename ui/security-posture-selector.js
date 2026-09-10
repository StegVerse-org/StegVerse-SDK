(function(root){
  "use strict";
  var ORDER=["SECURE","HIGH","HIGHEST"];
  function rank(t){return ORDER.indexOf(String(t||""));}
  function render(el,model,onSelect){
    if(!el||!model) throw new Error("security_posture_model_required");
    var automatic=model.automatic_posture&&model.automatic_posture.tier||null;
    var effective=model.effective_posture&&model.effective_posture.tier||null;
    var selectionPresent=!!(model.selected_posture&&model.selected_posture.selection_present!==false)||model.selection_present===true;
    var selected=selectionPresent&&model.selected_posture?model.selected_posture.tier:(selectionPresent?model.selected_tier:null);
    var authoritative=model.resolution_authority==="INTERLOCK_INTR"&&automatic&&effective;
    var floor=authoritative?automatic:null;
    el.innerHTML="";
    el.classList.add("sv-security-posture");
    var summary=document.createElement("div");
    summary.className="sv-security-posture-summary";
    summary.innerHTML="<strong>Security posture</strong><span data-role='effective'>"+(effective||"Awaiting InTr")+"</span>";
    var detail=document.createElement("div");
    detail.className="sv-security-posture-detail";
    detail.innerHTML="<span>Automatic: <strong data-role='automatic'>"+(automatic||"Awaiting InTr")+"</strong></span><span>Selected: <strong data-role='selected'>"+(selected||"Automatic")+"</strong></span><span>Authority: <strong data-role='authority'>"+(authoritative?"Interlock/InTr":"Pending")+"</strong></span>";
    var select=document.createElement("select");
    select.setAttribute("aria-label","Select requested security posture");
    var autoOpt=document.createElement("option"); autoOpt.value=""; autoOpt.textContent="Automatic (ecosystem floor)"; autoOpt.selected=!selectionPresent; select.appendChild(autoOpt);
    ORDER.forEach(function(t){
      var opt=document.createElement("option"); opt.value=t; opt.textContent=t;
      opt.disabled=!!floor&&rank(t)<rank(floor); opt.selected=selectionPresent&&t===selected; select.appendChild(opt);
    });
    select.addEventListener("change",function(){
      if(select.value&&floor&&rank(select.value)<rank(floor)){select.value=selected||"";return;}
      selectionPresent=select.value!=="";
      selected=selectionPresent?select.value:null;
      detail.querySelector("[data-role='selected']").textContent=selected||"Automatic";
      if(typeof onSelect==="function") onSelect(selected);
    });
    el.appendChild(summary); el.appendChild(detail); el.appendChild(select);
  }
  root.StegVerseSecurityPostureSelector={render:render,rank:rank,tiers:ORDER.slice()};
})(typeof globalThis!=="undefined"?globalThis:this);
