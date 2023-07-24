const toggleRouteModal = document.getElementById('toggleRouteModal')
toggleRouteModal.addEventListener('show.bs.modal', event => {
  const button = event.relatedTarget

  const route_id = button.getAttribute('data-bs-route-id')
  const route_enabled = button.getAttribute('data-bs-route-enabled')
  const route = button.getAttribute('data-bs-route')
  const label = toggleRouteModal.querySelector('#toggleRouteModalLabel')
  const info_text = toggleRouteModal.querySelector('#toggleRouteModalInfoText')
  const submit_button = toggleRouteModal.querySelector('#toggleRouteModalSubmitButton')
  const route_id_input = toggleRouteModal.querySelector('#toggleRouteModalRouteID')
  const route_enabled_input = toggleRouteModal.querySelector('#toggleRouteModalRouteEnabled')

  route_id_input.value = route_id
  route_enabled_input.value = route_enabled
  if (route_enabled === "True") {
    info_text.textContent = 'Disable the route "' + route + '"?'
    label.textContent = 'Disable route'
    submit_button.classList.add("btn-danger")
    submit_button.classList.remove("btn-primary")
    submit_button.textContent = 'Disable route'
  } else {
    info_text.textContent = 'Enable the route "' + route + '"?'
    label.textContent = 'Enable route'
    submit_button.classList.add("btn-primary")
    submit_button.classList.remove("btn-danger")
    submit_button.textContent = 'Enable route'
  }
})

const deleteProbeModal = document.getElementById('deleteProbeModal')
deleteProbeModal.addEventListener('show.bs.modal', event => {
  const button = event.relatedTarget

  const probe_id = button.getAttribute('data-bs-probe-id')
  const probe_name = button.getAttribute('data-bs-probe-name')
  const label = deleteProbeModal.querySelector('#deleteProbeModalLabel')
  const info_text = deleteProbeModal.querySelector('#deleteProbeModalInfoText')
  const probe_id_input = deleteProbeModal.querySelector('#deleteProbeModalProbeID')

  probe_id_input.value = probe_id
  label.textContent = 'Delete probe ' + probe_name
  info_text.textContent = 'Are you sure that you want to delete ' + probe_name + '?'
})

const editProbeModal = document.getElementById('editProbeModal')
editProbeModal.addEventListener('show.bs.modal', event => {
  const button = event.relatedTarget

  const probe_id = button.getAttribute('data-bs-probe-id')
  const probe_name = button.getAttribute('data-bs-probe-name')
  const iperf3_enabled = button.getAttribute('data-bs-test-iperf3-enabled')
  const iperf3_bandwidth = button.getAttribute('data-bs-test-iperf3-bandwidth')
  const label = editProbeModal.querySelector('#editProbeModalLabel')
  const probe_id_input = editProbeModal.querySelector('#id_probe_id')
  const iperf3_enabled_input = editProbeModal.querySelector('#id_iperf3_enabled')
  const iperf3_bandwidth_input = editProbeModal.querySelector('#id_iperf3_bandwidth_limit')

  probe_id_input.value = probe_id
  label.textContent = 'Edit probe ' + probe_name
  iperf3_bandwidth_input.value = iperf3_bandwidth
  if (iperf3_enabled === "True") {
    iperf3_enabled_input.checked = true
  } else {
    iperf3_enabled_input.checked = false
  }
})