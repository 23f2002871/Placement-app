const { createApp } = Vue;
const { createRouter, createWebHashHistory } = VueRouter;

// ---- COMPONENTS ----

const LoginPage = { 
    template: `
        <div class="row justify-content-center">
            <div class="col-md-5">
                <div class="card shadow mt-4">
                    <div class="card-body">
                        <h3 class="card-title text-center mb-4">User Login</h3>
                        <form @submit.prevent="submitLogin">
                            <div class="mb-3">
                                <label>Username</label>
                                <input v-model="loginData.username" type="text" class="form-control" required>
                            </div>
                            <div class="mb-4">
                                <label>Password</label>
                                <input v-model="loginData.password" type="password" class="form-control" required>
                            </div>
                            <button type="submit" class="btn btn-primary w-100">Login to Dashboard</button>
                        </form>
                        <div class="mt-3 text-center small text-muted">
                            <p>Don't have an account? <router-link to="/register">Register here</router-link></p>
                        </div>
                    </div>
                </div>
            </div>
        </div>`,
    data() { return { loginData: { username: '', password: '' } } },
    methods: {
        async submitLogin() {
            try {
                const response = await axios.post('/api/auth/login', this.loginData);
                localStorage.setItem('userToken', response.data.access_token);
                localStorage.setItem('userRole', response.data.role);
                this.$root.userIsLoggedIn = true;
                if (response.data.role === 'admin') this.$router.push('/admin');
                else if (response.data.role === 'student') this.$router.push('/student');
                else this.$router.push('/company');
            } catch (error) { alert("Invalid username or password"); }
        }
    }
};

const RegisterPage = {
    template: `
        <div class="row justify-content-center">
            <div class="col-md-5">
                <div class="card shadow mt-4">
                    <div class="card-body">
                        <h3 class="card-title text-center mb-4">Register New Account</h3>
                        <div class="mb-3">
                            <label>I am a...</label>
                            <select v-model="selectedRole" class="form-select">
                                <option value="student">Student</option>
                                <option value="company">Company</option>
                            </select>
                        </div>
                        <form @submit.prevent="submitRegistration">
                            <input v-model="regData.username" type="text" class="form-control mb-3" placeholder="Choose a Username" required>
                            <input v-model="regData.email" type="email" class="form-control mb-3" placeholder="Your Email Address" required>
                            <input v-model="regData.password" type="password" class="form-control mb-3" placeholder="Choose a Password" required>
                            <div v-if="selectedRole === 'company'" class="border p-3 mb-3 bg-light rounded">
                                <h6 class="mb-3">Company Details</h6>
                                <input v-model="regData.company_name" type="text" class="form-control mb-2" placeholder="Organization Name" required>
                                <input v-model="regData.hr_contact" type="text" class="form-control" placeholder="HR Person Name" required>
                            </div>
                            <button type="submit" class="btn btn-success w-100">Register</button>
                        </form>
                    </div>
                </div>
            </div>
        </div>`,
    data() { return { selectedRole: 'student', regData: { username: '', email: '', password: '', company_name: '', hr_contact: '' } } },
    methods: {
        async submitRegistration() {
            let apiURL = this.selectedRole === 'company' ? '/api/auth/register/company' : '/api/auth/register/student';
            try {
                const response = await axios.post(apiURL, this.regData);
                alert(response.data.msg);
                this.$router.push('/'); 
            } catch (error) { alert(error.response.data.msg); }
        }
    }
};

const AdminView = {
    template: `<div>
        <div class="d-flex justify-content-between align-items-center mb-4 border-bottom pb-2">
            <h2 class="mb-0">Admin Dashboard</h2>
            <input v-model="adminSearchQuery" type="text" class="form-control w-25" placeholder="Search users...">
        </div>
        
        <div class="row">
            <div class="col-md-6">
                <div class="card shadow mb-4">
                    <div class="card-header bg-dark text-white">Registered Companies</div>
                    <div class="card-body p-0">
                        <ul class="list-group list-group-flush">
                            <li v-for="c in filteredCompanies" :key="c.id" class="list-group-item d-flex justify-content-between align-items-center">
                                <span :class="{'text-decoration-line-through text-muted': !c.is_active}">{{ c.name }}</span>
                                <div>
                                    <button @click="viewProfile(c, 'company')" class="btn btn-sm btn-info me-2">Profile</button>
                                    <button @click="blockUser(c.id)" :class="c.is_active ? 'btn btn-sm btn-danger' : 'btn btn-sm btn-secondary'">{{ c.is_active ? 'blacklist' : 'restore' }}</button>
                                </div>
                            </li>
                        </ul>
                    </div>
                </div>

                <div class="card shadow mb-4">
                    <div class="card-header bg-dark text-white">Registered Students</div>
                    <div class="card-body p-0">
                        <ul class="list-group list-group-flush">
                            <li v-for="s in filteredStudents" :key="s.id" class="list-group-item d-flex justify-content-between align-items-center">
                                <span :class="{'text-decoration-line-through text-muted': !s.is_active}">{{ s.username }}</span>
                                <div>
                                    <button @click="viewProfile(s, 'student')" class="btn btn-sm btn-info me-2">Profile</button>
                                    <button @click="blockUser(s.id)" :class="s.is_active ? 'btn btn-sm btn-danger' : 'btn btn-sm btn-secondary'">{{ s.is_active ? 'blacklist' : 'restore' }}</button>
                                </div>
                            </li>
                        </ul>
                    </div>
                </div>
                
                <div v-if="selectedDetails" class="card shadow mb-4 border-info">
                    <div class="card-header bg-info text-dark fw-bold">Detailed Information</div>
                    <div class="card-body">
                        <h5 v-if="detailsType === 'student'">Student: {{ selectedDetails.username }}</h5>
                        <div v-if="detailsType === 'student'">
                            <p><strong>Department:</strong> {{ selectedDetails.department }}</p>
                            <p><strong>CGPA:</strong> {{ selectedDetails.cgpa }}</p>
                            <p v-if="selectedDetails.resume_path"><a :href="'/uploads/resumes/' + selectedDetails.resume_path" target="_blank" class="btn btn-sm btn-primary">Download Resume</a></p>
                            <p v-else class="text-danger small">No resume uploaded.</p>
                        </div>
                        
                        <h5 v-if="detailsType === 'company'">Company: {{ selectedDetails.name }}</h5>
                        <div v-if="detailsType === 'company'">
                            <p><strong>HR Contact Person:</strong> {{ selectedDetails.hr_contact }}</p>
                        </div>
                        <button @click="selectedDetails = null" class="btn btn-sm btn-secondary mt-2">Close Panel</button>
                    </div>
                </div>

                <div class="card shadow mb-4 border-warning">
                    <div class="card-header bg-warning text-dark fw-bold">Pending Approvals</div>
                    <div class="card-body">
                        <h6 class="text-muted">Companies Waiting</h6>
                        <ul class="list-group mb-3">
                            <li v-for="c in waitingCompanies" :key="c.id" class="list-group-item d-flex justify-content-between p-2">
                                {{ c.name }} <button @click="acceptCompany(c.id)" class="btn btn-sm btn-success">Approve</button>
                            </li>
                        </ul>
                        <h6 class="text-muted">Drives Waiting</h6>
                        <ul class="list-group">
                            <li v-for="d in waitingDrives" :key="d.id" class="list-group-item d-flex justify-content-between p-2">
                                {{ d.title }} <button @click="acceptDrive(d.id)" class="btn btn-sm btn-success">Approve</button>
                            </li>
                        </ul>
                    </div>
                </div>
            </div>

            <div class="col-md-6">
                <div class="card shadow mb-4">
                    <div class="card-header bg-dark text-white">Ongoing Drives</div>
                    <div class="card-body p-0">
                        <table class="table mb-0 table-hover">
                            <thead><tr><th>Drive Name</th><th>Company</th><th>Actions</th></tr></thead>
                            <tbody>
                                <tr v-for="d in allDrivesList" :key="d.id">
                                    <td>{{ d.title }}</td><td>{{ d.company }}</td>
                                    <td><button @click="showDriveData(d)" class="btn btn-sm btn-outline-info">view details</button></td>
                                </tr>
                            </tbody>
                        </table>
                        <div v-if="clickedDrive" class="p-3 bg-light border-top">
                            <h5>Details: {{ clickedDrive.title }}</h5>
                            <p>Description: {{ clickedDrive.description }}</p>
                            <p>Status: {{ clickedDrive.status }}</p>
                            <button @click="clickedDrive = null" class="btn btn-sm btn-dark">Close</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>`,
    data() { 
        return { 
            adminSearchQuery: '', waitingCompanies: [], waitingDrives: [],
            studentList: [], approvedCompaniesList: [], allDrivesList: [], allAppsList: [],
            clickedDrive: null, selectedDetails: null, detailsType: ''
        } 
    },
    computed: {
        filteredStudents() {
            if (!this.adminSearchQuery) return this.studentList;
            return this.studentList.filter(s => s.username.toLowerCase().includes(this.adminSearchQuery.toLowerCase()));
        },
        filteredCompanies() {
            if (!this.adminSearchQuery) return this.approvedCompaniesList;
            return this.approvedCompaniesList.filter(c => c.name.toLowerCase().includes(this.adminSearchQuery.toLowerCase()));
        }
    },
    methods: {
        getTokenHeader() { return { headers: { Authorization: 'Bearer ' + localStorage.getItem('userToken') } }; },
        async loadAdminData() {
            const h = this.getTokenHeader();
            this.waitingCompanies = (await axios.get('/api/admin/pending-companies', h)).data;
            this.waitingDrives = (await axios.get('/api/admin/pending-drives', h)).data;
            this.studentList = (await axios.get('/api/admin/students', h)).data;
            this.approvedCompaniesList = (await axios.get('/api/admin/companies', h)).data;
            this.allDrivesList = (await axios.get('/api/admin/all-drives', h)).data;
            this.allAppsList = (await axios.get('/api/admin/all-applications', h)).data;
        },
        async acceptCompany(id) { await axios.post('/api/admin/approve-company/'+id, {}, this.getTokenHeader()); this.loadAdminData(); },
        async acceptDrive(id) { await axios.post('/api/admin/approve-drive/'+id, {}, this.getTokenHeader()); this.loadAdminData(); },
        async blockUser(id) { await axios.post('/api/admin/blacklist/'+id, {}, this.getTokenHeader()); this.loadAdminData(); },
        showDriveData(driveData) { this.clickedDrive = driveData; },
        viewProfile(dataObj, type) { this.selectedDetails = dataObj; this.detailsType = type; }
    }, 
    mounted() { this.loadAdminData(); }
};

const CompanyView = {
    template: `<div>
        <div class="d-flex justify-content-between align-items-center mb-4 border-bottom pb-2">
            <h2 class="mb-0">Welcome {{ myCompanyName }}</h2>
            <input v-if="activeScreen === 'homeDashboard'" v-model="companySearchQuery" type="text" class="form-control w-25" placeholder="Search your drives...">
        </div>

        <div v-if="activeScreen === 'homeDashboard'">
            <div class="card shadow mb-4">
                <div class="card-header bg-dark text-white d-flex justify-content-between align-items-center">
                    Upcoming Drives
                    <button @click="activeScreen = 'newDriveForm'" class="btn btn-sm btn-light text-dark fw-bold">Create Drive</button>
                </div>
                <div class="card-body p-0">
                    <table class="table table-hover mb-0">
                        <thead><tr><th>Sr No.</th><th>Drive Name</th><th>Actions</th></tr></thead>
                        <tbody>
                            <tr v-for="(d, i) in getOpenDrives" :key="d.id">
                                <td>{{ i + 1 }}</td>
                                <td>{{ d.title }} <span v-if="d.status==='Pending'" class="badge bg-warning text-dark ms-2">Pending</span></td>
                                <td>
                                    <button v-if="d.status==='Approved'" @click="openDriveDetails(d)" class="btn btn-sm btn-outline-primary me-2">view details</button>
                                    <button v-if="d.status==='Approved'" @click="markCompleted(d.id)" class="btn btn-sm btn-outline-success">mark as complete</button>
                                </td>
                            </tr>
                            <tr v-if="getOpenDrives.length === 0"><td colspan="3" class="text-center text-muted py-3">No drives match your search.</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <div class="card shadow mb-4">
                <div class="card-header bg-secondary text-white">Closed Drives</div>
                <div class="card-body p-0">
                    <table class="table mb-0">
                        <thead><tr><th>Sr No.</th><th>Drive Name</th><th>Actions</th></tr></thead>
                        <tbody>
                            <tr v-for="(d, i) in getClosedDrives" :key="d.id">
                                <td>{{ i + 1 }}</td>
                                <td>{{ d.title }}</td>
                                <td><button @click="openDriveDetails(d)" class="btn btn-sm btn-outline-info">update</button></td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <div v-if="activeScreen === 'newDriveForm'" class="row justify-content-center">
            <div class="col-md-7">
                <div class="card shadow">
                    <div class="card-header bg-primary text-white">Create a Drive</div>
                    <div class="card-body">
                        <form @submit.prevent="submitNewDrive">
                            <input v-model="newDriveData.job_title" class="form-control mb-3" placeholder="Job Title" required>
                            <textarea v-model="newDriveData.job_description" class="form-control mb-3" placeholder="Job Description" required></textarea>
                            <input v-model="newDriveData.eligibility_criteria" class="form-control mb-3" placeholder="Eligibility Criteria" required>
                            <input v-model="newDriveData.location" class="form-control mb-3" placeholder="Location" required>
                            <input v-model="newDriveData.salary" type="number" class="form-control mb-3" placeholder="Salary" required>
                            <label class="form-label small">Application Deadline</label>
                            <input v-model="newDriveData.deadline" type="date" class="form-control mb-4" required>
                            <div class="d-flex justify-content-between">
                                <button type="button" @click="activeScreen = 'homeDashboard'" class="btn btn-secondary px-4">Cancel</button>
                                <button type="submit" class="btn btn-success px-4">Save</button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>

        <div v-if="activeScreen === 'appReviewList'" class="card shadow">
            <div class="card-header bg-dark text-white">Update Applications for the Drive</div>
            <div class="card-body">
                <h5>Job Title: {{ clickedDrive.title }}</h5>
                <hr>
                <h6>Received Applications</h6>
                <ul class="list-group mb-4">
                    <li v-for="app in driveAppsList" :key="app.app_id" class="list-group-item d-flex justify-content-between align-items-center">
                        <div>{{ app.student_name }} - <span class="text-muted">{{ app.status }}</span></div>
                        <button @click="reviewSingleApp(app)" class="btn btn-sm btn-outline-primary">review application</button>
                    </li>
                </ul>
                <button @click="activeScreen = 'homeDashboard'" class="btn btn-secondary">Back</button>
            </div>
        </div>

        <div v-if="activeScreen === 'singleAppReview'" class="row justify-content-center">
            <div class="col-md-6">
                <div class="card shadow border-dark">
                    <div class="card-body p-4">
                        <h3 class="mb-4 text-center">Student Application</h3>
                        <p><strong>Name:</strong> {{ clickedApp.student_name }}</p>
                        <p><strong>Department:</strong> {{ clickedApp.department }}</p>
                        <p><strong>CGPA:</strong> {{ clickedApp.cgpa }}</p>
                        <p><strong>Status:</strong> {{ clickedApp.status }}</p>
                        
                        <div class="mb-3">
                            <a v-if="clickedApp.resume_path" :href="'/uploads/resumes/' + clickedApp.resume_path" target="_blank" class="btn btn-sm btn-primary">
                                View Student Resume (PDF)
                            </a>
                            <span v-else class="text-danger small">No resume uploaded.</span>
                        </div>
                        
                        <div class="mt-4 border-top pt-3">
                            <label>Update Status:</label>
                            <select v-model="tempStatus" class="form-select mb-3">
                                <option value="Applied">Waiting</option>
                                <option value="Shortlisted">Shortlist</option>
                                <option value="Selected">Select</option>
                                <option value="Rejected">Reject</option>
                            </select>
                            <button @click="saveNewStatus" class="btn btn-success w-100 mb-2">Save Status</button>
                            <button @click="activeScreen = 'appReviewList'" class="btn btn-outline-dark w-100">Back</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>`,
    data() { return { companySearchQuery: '', myCompanyName: 'Company', activeScreen: 'homeDashboard', newDriveData: {job_title:'', job_description:'', eligibility_criteria:'', location:'', salary:'', deadline:''}, myDrivesList: [], driveAppsList: [], clickedDrive: null, clickedApp: null, tempStatus: '' } },
    computed: {
        getOpenDrives() { 
            let openDrives = this.myDrivesList.filter(d => d.status !== 'Closed');
            if (this.companySearchQuery) return openDrives.filter(d => d.title.toLowerCase().includes(this.companySearchQuery.toLowerCase()));
            return openDrives;
        },
        getClosedDrives() { 
            let closedDrives = this.myDrivesList.filter(d => d.status === 'Closed'); 
            if (this.companySearchQuery) return closedDrives.filter(d => d.title.toLowerCase().includes(this.companySearchQuery.toLowerCase()));
            return closedDrives;
        }
    },
    methods: {
        getToken() { return { headers: { Authorization: 'Bearer ' + localStorage.getItem('userToken') } }; },
        async loadCompanyData() { 
            try {
                const info = await axios.get('/api/company/me', this.getToken());
                this.myCompanyName = info.data.company_name;
                const drives = await axios.get('/api/company/drives', this.getToken());
                this.myDrivesList = drives.data;
            } catch(err) { console.log(err); }
        },
        async submitNewDrive() { 
            try {
                await axios.post('/api/company/drives', this.newDriveData, this.getToken()); 
                this.newDriveData = {job_title:'', job_description:'', eligibility_criteria:'', location:'', salary:'', deadline:''};
                this.activeScreen = 'homeDashboard'; this.loadCompanyData(); 
            } catch(err) { alert("Failed"); }
        },
        async markCompleted(id) { await axios.put('/api/company/drives/'+id+'/close', {}, this.getToken()); this.loadCompanyData(); },
        async openDriveDetails(drive) { 
            this.clickedDrive = drive; 
            const res = await axios.get('/api/company/drives/'+drive.id+'/applications', this.getToken());
            this.driveAppsList = res.data; this.activeScreen = 'appReviewList';
        },
        reviewSingleApp(app) { this.clickedApp = app; this.tempStatus = app.status; this.activeScreen = 'singleAppReview'; },
        async saveNewStatus() { 
            await axios.put('/api/company/applications/'+this.clickedApp.app_id+'/status', {status: this.tempStatus}, this.getToken()); 
            alert("Saved!");
            const res = await axios.get('/api/company/drives/'+this.clickedDrive.id+'/applications', this.getToken());
            this.driveAppsList = res.data; this.activeScreen = 'appReviewList'; 
        }
    }, mounted() { this.loadCompanyData(); }
};

const StudentView = {
    template: `<div>
        <div class="d-flex justify-content-between align-items-center mb-4 border-bottom pb-2">
            <h2 class="mb-0">Welcome Student</h2>
            <input v-if="viewMode !== 'driveInfo' && viewMode !== 'profile'" v-model="studentSearchQuery" type="text" class="form-control w-25 mx-3" placeholder="Search companies or jobs...">
            <div>
                <button @click="viewMode = 'main'" :class="viewMode === 'main' ? 'btn btn-primary' : 'btn btn-outline-primary'">Dashboard</button>
                <button @click="openMyProfile" :class="viewMode === 'profile' ? 'btn btn-secondary ms-2' : 'btn btn-outline-secondary ms-2'">Manage Profile</button>
                <button @click="viewMode = 'history'" :class="viewMode === 'history' ? 'btn btn-info ms-2' : 'btn btn-outline-info ms-2'">History</button>
                <button @click="doExport" class="btn btn-dark ms-2">Export CSV</button>
            </div>
        </div>
        
        <div v-if="viewMode === 'main'" class="row">
            <div class="col-md-5">
                <div class="card shadow mb-4">
                    <div class="card-header bg-dark text-white">Organizations</div>
                    <div class="card-body p-0">
                        <ul class="list-group list-group-flush">
                            <li v-for="c in filteredOrgs" :key="c.id" class="list-group-item d-flex justify-content-between align-items-center">
                                {{ c.name }}
                                <button @click="pickCompany(c)" class="btn btn-sm btn-outline-primary">View Details</button>
                            </li>
                        </ul>
                        <div v-if="filteredOrgs.length === 0" class="p-3 text-muted text-center">No organizations match your search.</div>
                    </div>
                </div>
            </div>
            
            <div class="col-md-7">
                <div v-if="activeCompany" class="card shadow mb-4">
                    <div class="card-header bg-success text-white">Current Drives for {{ activeCompany.name }}</div>
                    <div class="card-body p-0">
                        <div class="bg-light p-2 border-bottom text-muted small">
                            <strong>HR Contact Person:</strong> {{ activeCompany.hr_contact }}
                        </div>
                        <ul class="list-group list-group-flush">
                            <li v-for="d in filteredDrives" :key="d.id" class="list-group-item d-flex justify-content-between align-items-center">
                                {{ d.title }}
                                <button @click="seeDriveInfo(d)" class="btn btn-sm btn-info">View Details</button>
                            </li>
                        </ul>
                        <div v-if="filteredDrives.length === 0" class="p-3 text-muted">No drives match your search.</div>
                    </div>
                </div>
                <div v-else class="alert alert-secondary">Select an Organization to see their jobs.</div>
            </div>
        </div>

        <div v-if="viewMode === 'profile'" class="row justify-content-center">
            <div class="col-md-7">
                <div class="card shadow border-0">
                    <div class="card-header bg-info text-dark fw-bold text-center">Student Academic Profile</div>
                    <div class="card-body bg-white p-4">
                        <form @submit.prevent="submitProfileData">
                            <div class="mb-3">
                                <label class="fw-semibold small text-muted">Student Full Name</label>
                                <input v-model="studentInfoDetails.full_name" type="text" class="form-control" placeholder="Enter your full name">
                            </div>
                            <div class="mb-3">
                                <label class="fw-semibold small text-muted">Academic Department</label>
                                <input v-model="studentInfoDetails.department" type="text" class="form-control" placeholder="e.g., Computer Science">
                            </div>
                            <div class="mb-3">
                                <label class="fw-semibold small text-muted">Current CGPA</label>
                                <input v-model="studentInfoDetails.cgpa" type="number" step="0.01" class="form-control" placeholder="e.g., 9.2">
                            </div>
                            <div class="mb-4">
                                <label class="fw-semibold small text-muted">Resume Document (PDF only)</label>
                                <input type="file" @change="captureFile" accept=".pdf" class="form-control">
                                <div v-if="studentInfoDetails.resume_path" class="text-primary small mt-2">
                                    <i>Uploaded file: {{ studentInfoDetails.resume_path }}</i>
                                </div>
                            </div>
                            <div class="d-grid gap-2">
                                <button type="submit" class="btn btn-success">Update Details</button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>

        <div v-if="viewMode === 'driveInfo'" class="row justify-content-center">
            <div class="col-md-8">
                <div class="card shadow">
                    <div class="card-body">
                        <h3>{{ activeDrive.title }}</h3>
                        <h5 class="text-muted mb-4">{{ activeDrive.company }}</h5>
                        <p><strong>Description:</strong> {{ activeDrive.description }}</p>
                        <p><strong>Eligibility:</strong> {{ activeDrive.eligibility }}</p>
                        <p><strong>Salary:</strong> {{ activeDrive.salary }}</p>
                        <p><strong>Location:</strong> {{ activeDrive.location }}</p>
                        <p class="text-danger small">Deadline: {{ activeDrive.deadline }}</p>
                        <div class="mt-4 pt-3 border-top">
                            <button @click="sendApplication(activeDrive.id)" class="btn btn-primary px-4">Apply</button>
                            <button @click="viewMode = 'main'" class="btn btn-outline-dark ms-3">Go Back</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div v-if="viewMode === 'history'">
            <div class="card shadow mb-4">
                <div class="card-header bg-dark text-white">Student Application History</div>
                <div class="card-body p-0">
                    <table class="table table-striped mb-0">
                        <thead>
                            <tr><th>Drive No.</th><th>Company</th><th>Job Title</th><th>Date</th><th>Results</th></tr>
                        </thead>
                        <tbody>
                            <tr v-for="a in filteredHistory" :key="a.id">
                                <td>{{ a.id }}</td>
                                <td>{{ a.company }}</td>
                                <td>{{ a.drive_title }}</td>
                                <td>{{ a.date }}</td>
                                <td><strong>{{ a.status }}</strong></td>
                            </tr>
                            <tr v-if="filteredHistory.length === 0"><td colspan="5" class="text-center py-3 text-muted">No history matches your search.</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>`,
    data() { 
        return { studentSearchQuery: '', viewMode: 'main', orgList: [], fullDriveList: [], historyApps: [], activeCompany: null, activeDrive: null, studentInfoDetails: { full_name: '', department: '', cgpa: '', resume_path: '' }, uploadedResumeDoc: null } 
    },
    computed: {
        filteredOrgs() { if (!this.studentSearchQuery) return this.orgList; return this.orgList.filter(o => o.name.toLowerCase().includes(this.studentSearchQuery.toLowerCase())); },
        filteredDrives() {
            if (this.activeCompany == null) return [];
            let companyDrives = this.fullDriveList.filter(d => d.company_id === this.activeCompany.id);
            if (this.studentSearchQuery) return companyDrives.filter(d => d.title.toLowerCase().includes(this.studentSearchQuery.toLowerCase()));
            return companyDrives;
        },
        filteredHistory() {
            if (!this.studentSearchQuery) return this.historyApps;
            const query = this.studentSearchQuery.toLowerCase();
            return this.historyApps.filter(a => a.company.toLowerCase().includes(query) || a.drive_title.toLowerCase().includes(query));
        }
    },
    methods: {
        getToken() { return { headers: { Authorization: 'Bearer ' + localStorage.getItem('userToken') } }; },
        async getStudentData() {
            const h = this.getToken();
            this.orgList = (await axios.get('/api/student/companies', h)).data;
            this.fullDriveList = (await axios.get('/api/student/drives', h)).data;
            this.historyApps = (await axios.get('/api/student/applications', h)).data;
        },
        async openMyProfile() {
            this.viewMode = 'profile';
            try {
                const res = await axios.get('/api/student/profile', this.getToken());
                this.studentInfoDetails = res.data;
            } catch(e) { console.log(e); }
        },
        captureFile(event) { this.uploadedResumeDoc = event.target.files[0]; },
        async submitProfileData() {
            let dataForm = new FormData();
            dataForm.append('full_name', this.studentInfoDetails.full_name || '');
            dataForm.append('department', this.studentInfoDetails.department || '');
            dataForm.append('cgpa', this.studentInfoDetails.cgpa || '');
            if (this.uploadedResumeDoc) dataForm.append('resume', this.uploadedResumeDoc);
            try {
                await axios.post('/api/student/profile', dataForm, { headers: { 'Authorization': 'Bearer ' + localStorage.getItem('userToken'), 'Content-Type': 'multipart/form-data' } });
                alert('Academic Profile has been updated successfully!');
                this.openMyProfile(); 
            } catch(err) { alert("Failed to update profile."); }
        },
        pickCompany(c) { this.activeCompany = c; },
        seeDriveInfo(d) { this.activeDrive = d; this.viewMode = 'driveInfo'; },
        async sendApplication(id) { 
            try {
                await axios.post('/api/student/apply/'+id, {}, this.getToken()); 
                alert("Applied!"); this.getStudentData(); this.viewMode = 'history'; 
            } catch(err) { alert(err.response.data.msg); }
        },
        async doExport() { 
            const res = await axios.post('/api/student/export-csv', {}, this.getToken());
            alert(res.data.msg); 
        }
    }, mounted() { this.getStudentData(); }
};

const myRouter = createRouter({
    history: createWebHashHistory(),
    routes: [
        { path: '/', component: LoginPage }, { path: '/register', component: RegisterPage },
        { path: '/admin', component: AdminView }, { path: '/student', component: StudentView }, { path: '/company', component: CompanyView }
    ]
});

myRouter.beforeEach((to, from, next) => {
    const hasToken = localStorage.getItem('userToken');
    const myRole = localStorage.getItem('userRole');
    if (to.path !== '/' && to.path !== '/register' && !hasToken) next('/');
    else if (to.path === '/admin' && myRole !== 'admin') next('/');
    else if (to.path === '/student' && myRole !== 'student') next('/');
    else if (to.path === '/company' && myRole !== 'company') next('/');
    else next();
});

const myApp = createApp({
    data() { return { userIsLoggedIn: false } },
    methods: { 
        handleLogout() { 
            localStorage.removeItem('userToken'); localStorage.removeItem('userRole'); 
            this.userIsLoggedIn = false; this.$router.push('/'); 
        } 
    },
    watch: { 
        $route() { this.userIsLoggedIn = localStorage.getItem('userToken') != null; } 
    },
    mounted() { this.userIsLoggedIn = localStorage.getItem('userToken') != null; }
});

myApp.use(myRouter); 
myApp.mount('#app');